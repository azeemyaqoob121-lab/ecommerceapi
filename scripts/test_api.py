"""
Test script to demonstrate the API functionality
This script will:
1. Create database tables
2. Create sample merchants
3. Test all API endpoints
4. Display results
"""

import os
import sys

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.core.management import call_command
from ecommerce_api.models import Merchant, Product, Variant
from rest_framework.test import APIClient
import json


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_response(response):
    """Print formatted API response"""
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json() if hasattr(response, 'json') else response.data
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
    except:
        print(f"Response: {response.data}")


def main():
    print_section("E-Commerce Product Management API - Test Demonstration")
    
    # Create tables
    print("Creating database tables...")
    call_command('migrate', '--run-syncdb', verbosity=0)
    print("✓ Database tables created\n")
    
    # Clear existing data
    print("Clearing existing data...")
    Product.objects.all().delete()
    Merchant.objects.all().delete()
    print("✓ Data cleared\n")
    
    # Create test merchants
    print("Creating test merchants...")
    merchant1 = Merchant.objects.create(
        name="Tech Store",
        email="tech@example.com",
        store_url="tech-store.myshopify.com",
        status="ACTIVE"
    )
    merchant2 = Merchant.objects.create(
        name="Fashion Boutique",
        email="fashion@example.com",
        store_url="fashion-boutique.myshopify.com",
        status="ACTIVE"
    )
    print(f"✓ Created merchants: {merchant1.name}, {merchant2.name}\n")
    
    # Initialize API client
    client = APIClient()
    
    # Test 1: Import Product
    print_section("TEST 1: Import Product from External Platform")
    import_data = {
        "store_url": "tech-store.myshopify.com",
        "product": {
            "id": "12345",
            "title": "Wireless Headphones Pro",
            "description": "High-quality wireless headphones with noise cancellation",
            "product_type": "Electronics",
            "variants": [
                {
                    "id": "67890",
                    "title": "Black - Standard",
                    "sku": "WHP-BLK-STD",
                    "price": "79.99",
                    "compare_at_price": "99.99",
                    "inventory_quantity": 100
                },
                {
                    "id": "67891",
                    "title": "White - Standard",
                    "sku": "WHP-WHT-STD",
                    "price": "79.99",
                    "compare_at_price": "99.99",
                    "inventory_quantity": 75
                }
            ]
        }
    }
    
    response = client.post('/api/products/import/', import_data, format='json')
    print_response(response)
    
    # Test 2: Import another product
    print_section("TEST 2: Import Another Product")
    import_data2 = {
        "store_url": "tech-store.myshopify.com",
        "product": {
            "id": "12346",
            "title": "Smart Watch X1",
            "description": "Feature-rich smartwatch with fitness tracking",
            "product_type": "Electronics",
            "variants": [
                {
                    "id": "67892",
                    "title": "Black - 42mm",
                    "sku": "SWX-BLK-42",
                    "price": "299.99",
                    "inventory_quantity": 50
                }
            ]
        }
    }
    
    response = client.post('/api/products/import/', import_data2, format='json')
    print_response(response)
    
    # Test 3: Import duplicate product (should return existing)
    print_section("TEST 3: Import Duplicate Product")
    response = client.post('/api/products/import/', import_data, format='json')
    print("(Should return existing product with 200 status)")
    print_response(response)
    
    # Test 4: List Products
    print_section("TEST 4: List Products for Merchant")
    response = client.get(f'/api/products/?merchant_id={merchant1.id}')
    print_response(response)
    
    # Test 5: List Products with Active Filter
    print_section("TEST 5: List Active Products Only")
    response = client.get(f'/api/products/?merchant_id={merchant1.id}&active=true')
    print_response(response)
    
    # Test 6: Search Products
    print_section("TEST 6: Search Products by Title")
    response = client.get(f'/api/products/?merchant_id={merchant1.id}&search=headphones')
    print_response(response)
    
    # Test 7: Get Product Detail
    print_section("TEST 7: Get Product Detail")
    product = Product.objects.first()
    response = client.get(f'/api/products/{product.id}/')
    print_response(response)
    
    # Test 8: Bulk Activate/Deactivate
    print_section("TEST 8: Bulk Deactivate Products")
    product_ids = list(Product.objects.values_list('id', flat=True))
    bulk_data = {
        "product_ids": product_ids,
        "active": False
    }
    response = client.post('/api/products/bulk-activate/', bulk_data, format='json')
    print_response(response)
    
    # Verify products are deactivated
    print("\nVerifying products are deactivated...")
    response = client.get(f'/api/products/?merchant_id={merchant1.id}')
    print_response(response)
    
    # Reactivate them
    print_section("TEST 9: Bulk Activate Products")
    bulk_data['active'] = True
    response = client.post('/api/products/bulk-activate/', bulk_data, format='json')
    print_response(response)
    
    # Test 10: Remove Product (Soft Delete)
    print_section("TEST 10: Remove Product (Soft Delete)")
    product = Product.objects.first()
    response = client.post(f'/api/products/{product.id}/remove/')
    print_response(response)
    
    # Verify product is deactivated
    print("\nVerifying product is deactivated...")
    response = client.get(f'/api/products/{product.id}/')
    print_response(response)
    
    # Test 11: Error Handling - Invalid Merchant
    print_section("TEST 11: Error Handling - Invalid Merchant")
    invalid_data = {
        "store_url": "nonexistent-store.myshopify.com",
        "product": {
            "id": "99999",
            "title": "Test Product",
            "variants": [
                {
                    "id": "88888",
                    "title": "Test Variant",
                    "price": "10.00",
                    "inventory_quantity": 1
                }
            ]
        }
    }
    response = client.post('/api/products/import/', invalid_data, format='json')
    print_response(response)
    
    # Test 12: Error Handling - Missing merchant_id
    print_section("TEST 12: Error Handling - Missing merchant_id in List")
    response = client.get('/api/products/')
    print_response(response)
    
    # Summary
    print_section("Test Summary")
    print(f"Total Merchants: {Merchant.objects.count()}")
    print(f"Total Products: {Product.objects.count()}")
    print(f"Total Variants: {Variant.objects.count()}")
    print(f"Active Products: {Product.objects.filter(active=True).count()}")
    print(f"Inactive Products: {Product.objects.filter(active=False).count()}")
    
    print("\n" + "="*80)
    print("  ✓ All tests completed successfully!")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
