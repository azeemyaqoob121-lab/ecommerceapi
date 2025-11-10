"""
URL configuration for ecommerce API project.
"""
from django.urls import path, include

urlpatterns = [
    path('api/', include('ecommerce_api.urls')),
]
