"""
Test script that makes actual HTTP requests to the running server
Run this after starting the server with: python manage.py runserver
"""

import requests
import json
import time


BASE_URL = "http://127.0.0.1:8000/api"


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_response(response):
    """Print formatted API response"""
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")


def check_server():
    """Check if server is running"""
    try:
        response = requests.get(BASE_URL + "/products/", timeout=2)
        return True
    except requests.exceptions.ConnectionError:
        return False


def main():
    print_section("E-Commerce Product Management API - Live Server Test")
    
    # Check if server is running
    print("Checking if server is running...")
    if not check_server():
        print("\n❌ ERROR: Server is not running!")
        print("\nPlease start the server in another terminal:")
        print("  python manage.py runserver")
        print("\nThen run this script again.")
        return
    
    print("✓ Server is running\n")
    
    # Wait a moment
    time.sleep(0.5)
    
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
    
    response = requests.post(f"{BASE_URL}/products/import/", json=import_data)
    print_response(response)
    
    # Get merchant_id from response
    merchant_id = response.json().get('merchant', {}).get('id') if response.status_code in [200, 201] else 1
    
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
    
    response = requests.post(f"{BASE_URL}/products/import/", json=import_data2)
    print_response(response)
    
    # Test 3: Import duplicate product
    print_section("TEST 3: Import Duplicate Product")
    response = requests.post(f"{BASE_URL}/products/import/", json=import_data)
    print("(Should return existing product)")
    print_response(response)
    
    # Test 4: List Products
    print_section("TEST 4: List Products for Merchant")
    response = requests.get(f"{BASE_URL}/products/?merchant_id={merchant_id}")
    print_response(response)
    
    # Get product IDs from response
    product_ids = []
    first_product_id = None
    if response.status_code == 200:
        results = response.json().get('results', [])
        product_ids = [p['id'] for p in results]
        first_product_id = product_ids[0] if product_ids else None
    
    # Test 5: List Active Products
    print_section("TEST 5: List Active Products Only")
    response = requests.get(f"{BASE_URL}/products/?merchant_id={merchant_id}&active=true")
    print_response(response)
    
    # Test 6: Search Products
    print_section("TEST 6: Search Products by Title")
    response = requests.get(f"{BASE_URL}/products/?merchant_id={merchant_id}&search=headphones")
    print_response(response)
    
    # Test 7: Get Product Detail
    if first_product_id:
        print_section("TEST 7: Get Product Detail")
        response = requests.get(f"{BASE_URL}/products/{first_product_id}/")
        print_response(response)
    
    # Test 8: Bulk Deactivate
    if product_ids:
        print_section("TEST 8: Bulk Deactivate Products")
        bulk_data = {
            "product_ids": product_ids,
            "active": False
        }
        response = requests.post(f"{BASE_URL}/products/bulk-activate/", json=bulk_data)
        print_response(response)
        
        # Verify deactivation
        print("\nVerifying products are deactivated...")
        response = requests.get(f"{BASE_URL}/products/?merchant_id={merchant_id}&active=false")
        print_response(response)
    
    # Test 9: Bulk Activate
    if product_ids:
        print_section("TEST 9: Bulk Activate Products")
        bulk_data = {
            "product_ids": product_ids,
            "active": True
        }
        response = requests.post(f"{BASE_URL}/products/bulk-activate/", json=bulk_data)
        print_response(response)
    
    # Test 10: Remove Product
    if first_product_id:
        print_section("TEST 10: Remove Product (Soft Delete)")
        response = requests.post(f"{BASE_URL}/products/{first_product_id}/remove/")
        print_response(response)
        
        # Verify removal
        print("\nVerifying product is deactivated...")
        response = requests.get(f"{BASE_URL}/products/{first_product_id}/")
        print_response(response)
    
    # Test 11: Error Handling
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
    response = requests.post(f"{BASE_URL}/products/import/", json=invalid_data)
    print_response(response)
    
    # Test 12: Missing merchant_id
    print_section("TEST 12: Error Handling - Missing merchant_id")
    response = requests.get(f"{BASE_URL}/products/")
    print_response(response)
    
    print_section("✓ All Tests Completed Successfully!")


if __name__ == '__main__':
    main()
