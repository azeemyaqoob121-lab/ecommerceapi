from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import transaction, IntegrityError
from django.db.models import Q, Prefetch
from decimal import Decimal

from .models import Product, Variant, Merchant
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ImportProductSerializer,
    BulkActivateSerializer
)


"""
Design Decisions and Assumptions:
1. Product Import:
   - Uses get_or_create to handle duplicate products gracefully
   - Calculates retail_price from compare_at_price or falls back to price
   - Uses bulk_create for variants for performance
   - Wrapped in transaction to ensure data consistency
   
2. Product Listing:
   - Implements pagination with page size of 20
   - Uses select_related to optimize merchant queries
   - Supports filtering by merchant_id, active status, and search
   
3. Product Detail:
   - Uses prefetch_related to avoid N+1 queries on variants
   - Different serializer from list view (includes full details)
   
4. Bulk Operations:
   - Uses update() for efficient bulk updates in single query
   - Returns count of affected records
   
5. Soft Delete:
   - Remove endpoint deactivates instead of deleting
   - Preserves data integrity for orders
   
6. Error Handling:
   - Validates merchant existence before import
   - Returns appropriate HTTP status codes
   - Provides clear error messages
"""


class ProductPagination(PageNumberPagination):
    """Custom pagination for product list"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations
    Implements all required endpoints with proper error handling and performance optimization
    """
    queryset = Product.objects.all()
    pagination_class = ProductPagination
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        """
        Optimize queries and implement filtering
        """
        queryset = Product.objects.select_related('merchant')
        
        # Filter by merchant_id (required for list view)
        merchant_id = self.request.query_params.get('merchant_id')
        if self.action == 'list' and not merchant_id:
            # Return empty queryset if merchant_id not provided for list
            return Product.objects.none()
        
        if merchant_id:
            queryset = queryset.filter(merchant_id=merchant_id)
        
        # Filter by active status
        active = self.request.query_params.get('active')
        if active is not None:
            if active.lower() == 'true':
                queryset = queryset.filter(active=True)
            elif active.lower() == 'false':
                queryset = queryset.filter(active=False)
        
        # Search by title
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        # Prefetch variants for detail view to avoid N+1 queries
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                Prefetch('variants', queryset=Variant.objects.all())
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list to enforce merchant_id requirement"""
        merchant_id = request.query_params.get('merchant_id')
        if not merchant_id:
            return Response(
                {'error': 'merchant_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate merchant exists
        try:
            Merchant.objects.get(id=merchant_id)
        except Merchant.DoesNotExist:
            return Response(
                {'error': f'Merchant with id {merchant_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'], url_path='import')
    def import_product(self, request):
        """
        POST /api/products/import/
        Import product from external platform (e.g., Shopify)
        """
        serializer = ImportProductSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        store_url = validated_data['store_url']
        product_data = validated_data['product']
        
        try:
            # Get merchant
            merchant = Merchant.objects.get(store_url=store_url)
            
            # Use transaction to ensure data consistency
            with transaction.atomic():
                # Create or get existing product
                product, created = Product.objects.get_or_create(
                    merchant=merchant,
                    external_id=product_data['id'],
                    defaults={
                        'title': product_data['title'],
                        'description': product_data.get('description', ''),
                        'product_type': product_data.get('product_type', ''),
                        'active': True,
                    }
                )
                
                # If product already exists, update it
                if not created:
                    product.title = product_data['title']
                    product.description = product_data.get('description', '')
                    product.product_type = product_data.get('product_type', '')
                    product.save()
                
                # Prepare variants for bulk creation
                variants_to_create = []
                existing_variant_ids = set(
                    product.variants.values_list('external_id', flat=True)
                )
                
                for variant_data in product_data['variants']:
                    # Skip if variant already exists
                    if variant_data['id'] in existing_variant_ids:
                        continue
                    
                    # Calculate retail_price
                    price = Decimal(str(variant_data['price']))
                    retail_price = price
                    
                    if variant_data.get('compare_at_price'):
                        retail_price = Decimal(str(variant_data['compare_at_price']))
                    
                    variants_to_create.append(Variant(
                        product=product,
                        external_id=variant_data['id'],
                        name=variant_data['title'],
                        sku=variant_data.get('sku', ''),
                        price=price,
                        retail_price=retail_price,
                        quantity=variant_data['inventory_quantity'],
                        active=True
                    ))
                
                # Bulk create variants for performance
                if variants_to_create:
                    Variant.objects.bulk_create(variants_to_create)
                
                # Update product base_price to minimum variant price
                min_price = min(
                    Decimal(str(v['price'])) 
                    for v in product_data['variants']
                )
                product.base_price = min_price
                product.save()
                
                # Return product with full details
                response_serializer = ProductDetailSerializer(product)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
                )
        
        except Merchant.DoesNotExist:
            return Response(
                {'error': f'Merchant with store_url {store_url} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except IntegrityError as e:
            return Response(
                {'error': f'Database integrity error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='bulk-activate')
    def bulk_activate(self, request):
        """
        POST /api/products/bulk-activate/
        Bulk activate or deactivate products
        """
        serializer = BulkActivateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product_ids = serializer.validated_data['product_ids']
        active = serializer.validated_data['active']
        
        try:
            # Update products in single query
            updated_count = Product.objects.filter(
                id__in=product_ids
            ).update(active=active)
            
            return Response({
                'message': f'Successfully updated {updated_count} products',
                'updated_count': updated_count,
                'active': active
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='remove')
    def remove_product(self, request, pk=None):
        """
        POST /api/products/{id}/remove/
        Soft delete product by deactivating it
        """
        try:
            product = self.get_object()
            product.active = False
            product.save()
            
            return Response({
                'message': f'Product "{product.title}" has been deactivated',
                'product_id': product.id
            }, status=status.HTTP_200_OK)
        
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
