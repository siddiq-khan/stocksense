from django.contrib import admin
from .models import Warehouse, Category, Product, StockItem

admin.site.register(Warehouse)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(StockItem)