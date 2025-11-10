# Quick Start Guide - E-Commerce API

## Step 1: Start the Server

Open Git Bash and run:

\`\`\`bash
python manage.py runserver
\`\`\`

You should see:
\`\`\`
Starting development server at http://127.0.0.1:8000/
\`\`\`

**Keep this terminal open - the server must stay running!**

## Step 2: Test the API

Open a **NEW** Git Bash terminal (keep the server running in the first one) and run:

\`\`\`bash
python scripts/test_with_server.py
\`\`\`

This will test all the API endpoints and show you the results.

## Available Endpoints

Once the server is running, you can test these endpoints:

### 1. Import Product
\`\`\`bash
curl -X POST http://127.0.0.1:8000/api/products/import/ \
  -H "Content-Type: application/json" \
  -d '{
    "store_url": "mystore.myshopify.com",
    "product": {
      "id": "12345",
      "title": "Test Product",
      "description": "A test product",
      "variants": [
        {
          "id": "67890",
          "title": "Default",
          "price": "19.99",
          "inventory_quantity": 100
        }
      ]
    }
  }'
\`\`\`

### 2. List Products
\`\`\`bash
curl "http://127.0.0.1:8000/api/products/?merchant_id=1"
\`\`\`

### 3. Get Product Detail
\`\`\`bash
curl http://127.0.0.1:8000/api/products/1/
\`\`\`

### 4. Search Products
\`\`\`bash
curl "http://127.0.0.1:8000/api/products/?merchant_id=1&search=test"
\`\`\`

### 5. Bulk Activate/Deactivate
\`\`\`bash
curl -X POST http://127.0.0.1:8000/api/products/bulk-activate/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_ids": [1, 2, 3],
    "active": false
  }'
\`\`\`

### 6. Remove Product
\`\`\`bash
curl -X POST http://127.0.0.1:8000/api/products/1/remove/
\`\`\`

## Browse the API in Your Browser

Visit: http://127.0.0.1:8000/api/products/

Django REST Framework provides a nice browsable interface where you can test all endpoints!

## Troubleshooting

**Port already in use?**
\`\`\`bash
python manage.py runserver 8080
\`\`\`

**Need to reset the database?**
\`\`\`bash
rm db.sqlite3
python manage.py migrate
\`\`\`

**Can't import 'rest_framework'?**
\`\`\`bash
pip install -r scripts/requirements.txt
