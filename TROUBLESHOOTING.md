# Troubleshooting Guide

## Issue: Getting 404 errors on all endpoints

### Solution Steps:

1. **Stop the Django server** (Press Ctrl+C in the terminal where it's running)

2. **Check registered URLs:**
   \`\`\`bash
   python scripts/check_urls.py
   \`\`\`

3. **Restart the server:**
   \`\`\`bash
   python manage.py runserver
   \`\`\`

4. **In a NEW terminal, run the test:**
   \`\`\`bash
   python scripts/test_with_server.py
   \`\`\`

### Alternative: Test with Browser

Visit these URLs in your browser to test manually:

- List products: http://127.0.0.1:8000/api/products/
- You should see a browsable API interface

### Alternative: Test with curl

\`\`\`bash
# Import a product
curl -X POST http://127.0.0.1:8000/api/products/import/ \
  -H "Content-Type: application/json" \
  -d '{"merchant_id": 1, "products": [{"name": "Test Product", "description": "Test", "price": "99.99", "variants": [{"sku": "TEST001", "stock": 5}]}]}'

# List products
curl http://127.0.0.1:8000/api/products/
\`\`\`

## Common Issues:

1. **Server not running**: Make sure `python manage.py runserver` is running
2. **Wrong URL**: Ensure you're using http://127.0.0.1:8000 not localhost
3. **Port conflict**: If port 8000 is busy, use: `python manage.py runserver 8080`
