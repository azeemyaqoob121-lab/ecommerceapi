#!/bin/bash

echo "================================================"
echo "  Django Server Restart and Test Script"
echo "================================================"
echo ""

echo "Step 1: Checking URL configuration..."
python scripts/check_urls.py

echo ""
echo "Step 2: Starting Django server..."
echo "Note: Press Ctrl+C to stop the server when done"
echo ""

python manage.py runserver
