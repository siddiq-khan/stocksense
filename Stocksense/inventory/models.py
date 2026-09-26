from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    unit_of_measure = models.CharField(max_length=20, default='pcs')  # e.g. pcs, kg, box
    reorder_point = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class StockItem(models.Model):
    """Per-location stock quantity — the single source of truth for 'how much is where'."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_items')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_items')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('product', 'warehouse')

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.name}: {self.quantity}"