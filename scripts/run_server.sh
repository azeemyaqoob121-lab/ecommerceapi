#!/bin/bash

echo "Starting Django Development Server..."
echo "=================================="
echo ""
echo "Server will be available at: http://127.0.0.1:8000"
echo "API Endpoints:"
echo "  - POST /api/products/import/"
echo "  - GET  /api/products/"
echo "  - GET  /api/products/{id}/"
echo "  - POST /api/products/bulk-activate/"
echo "  - POST /api/products/{id}/remove/"
echo ""
echo "Press CTRL+C to stop the server"
echo "=================================="
echo ""

python manage.py runserver
