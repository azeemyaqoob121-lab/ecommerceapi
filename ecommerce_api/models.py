from django.db import models

class Merchant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    store_url = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='products')
    external_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['merchant', 'external_id']
        indexes = [
            models.Index(fields=['merchant', 'active']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    external_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['product', 'external_id']
        indexes = [
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.product.title} - {self.name}"

class Order(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='orders')
    external_order_id = models.CharField(max_length=255, unique=True)
    order_number = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(Variant, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.quantity} x {self.variant.name}"
