# E-Commerce Product Management API

## Quick Start Guide

### Step 1: Run Migrations
\`\`\`bash
python manage.py makemigrations ecommerce_api
python manage.py migrate
\`\`\`

### Step 2: Start the Server
\`\`\`bash
# On Windows (Git Bash):
bash scripts/run_server.sh

# Or use the batch file:
scripts\run_server.bat

# Or run directly:
python manage.py runserver
\`\`\`

### Step 3: Test the API

**Option A: Run the Test Script**
Open a new terminal window and run:
\`\`\`bash
python scripts/test_api.py
\`\`\`

**Option B: Test with cURL**
\`\`\`bash
# Create a merchant first via Django shell
python manage.py shell
\`\`\`
\`\`\`python
from ecommerce_api.models import Merchant
Merchant.objects.create(name="Test Store", email="test@example.com", store_url="test-store.myshopify.com")
exit()
\`\`\`

\`\`\`bash
# Now test the import endpoint
curl -X POST http://127.0.0.1:8000/api/products/import/ \
  -H "Content-Type: application/json" \
  -d "{\"store_url\": \"test-store.myshopify.com\", \"product\": {\"id\": \"12345\", \"title\": \"Test Product\", \"variants\": [{\"id\": \"67890\", \"title\": \"Variant 1\", \"price\": \"19.99\", \"inventory_quantity\": 10}]}}"
\`\`\`

## API Endpoints

1. **Import Product**: `POST /api/products/import/`
2. **List Products**: `GET /api/products/?merchant_id=1`
3. **Get Product**: `GET /api/products/{id}/`
4. **Bulk Activate**: `POST /api/products/bulk-activate/`
5. **Remove Product**: `POST /api/products/{id}/remove/`

## Database Schema

- **Merchant**: Stores merchant information
- **Product**: Product catalog with merchant relationship
- **Variant**: Product variations with pricing and inventory
- **Order**: Order management
- **OrderItem**: Order line items
