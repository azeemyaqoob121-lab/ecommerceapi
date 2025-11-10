from rest_framework import serializers
from decimal import Decimal
from .models import Merchant, Product, Variant, Order, OrderItem


class VariantSerializer(serializers.ModelSerializer):
    """Serializer for Variant model with full details"""
    
    class Meta:
        model = Variant
        fields = [
            'id', 'external_id', 'name', 'sku', 'price', 
            'retail_price', 'quantity', 'active'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Minimal serializer for product list view"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'base_price', 'active', 'image_url']
    
    def get_image_url(self, obj):
        # Placeholder for image URL - would be from a related Image model in production
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer including all product fields and variants"""
    variants = VariantSerializer(many=True, read_only=True)
    merchant_name = serializers.CharField(source='merchant.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'external_id', 'title', 'description', 'product_type',
            'active', 'base_price', 'created_at', 'merchant_name', 
            'image_url', 'variants'
        ]
    
    def get_image_url(self, obj):
        return None


class ImportVariantSerializer(serializers.Serializer):
    """Serializer for validating incoming variant data during import"""
    id = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    sku = serializers.CharField(required=False, allow_blank=True, default='')
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    compare_at_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    inventory_quantity = serializers.IntegerField(required=True, min_value=0)


class ImportProductSerializer(serializers.Serializer):
    """Serializer for validating incoming product import data"""
    store_url = serializers.CharField(required=True)
    product = serializers.DictField(required=True)
    
    def validate_store_url(self, value):
        """Validate that merchant exists with this store_url"""
        try:
            Merchant.objects.get(store_url=value)
        except Merchant.DoesNotExist:
            raise serializers.ValidationError(
                f"No merchant found with store_url: {value}"
            )
        return value
    
    def validate_product(self, value):
        """Validate product structure"""
        if 'id' not in value:
            raise serializers.ValidationError("Product must have an 'id' field")
        if 'title' not in value:
            raise serializers.ValidationError("Product must have a 'title' field")
        if 'variants' not in value or not isinstance(value['variants'], list):
            raise serializers.ValidationError(
                "Product must have a 'variants' field with a list of variants"
            )
        
        # Validate each variant
        variant_serializer = ImportVariantSerializer(data=value['variants'], many=True)
        if not variant_serializer.is_valid():
            raise serializers.ValidationError({
                'variants': variant_serializer.errors
            })
        
        return value


class BulkActivateSerializer(serializers.Serializer):
    """Serializer for bulk activate/deactivate operation"""
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False
    )
    active = serializers.BooleanField(required=True)
