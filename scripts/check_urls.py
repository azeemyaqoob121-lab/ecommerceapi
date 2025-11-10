import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

def show_urls(urlpatterns, depth=0):
    """Recursively display all URL patterns"""
    for entry in urlpatterns:
        if isinstance(entry, URLPattern):
            print('  ' * depth + f'✓ {entry.pattern}')
        elif isinstance(entry, URLResolver):
            print('  ' * depth + f'├─ {entry.pattern}')
            show_urls(entry.url_patterns, depth + 1)

print("\n" + "="*80)
print("  Registered URL Patterns")
print("="*80 + "\n")

resolver = get_resolver()
show_urls(resolver.url_patterns)

print("\n" + "="*80)
print("  Available API Endpoints")
print("="*80 + "\n")
print("Base URL: http://127.0.0.1:8000")
print("\nEndpoints:")
print("  POST   /api/products/import/")
print("  GET    /api/products/")
print("  GET    /api/products/{id}/")
print("  POST   /api/products/bulk-activate/")
print("  POST   /api/products/{id}/remove/")
print("\n" + "="*80 + "\n")
