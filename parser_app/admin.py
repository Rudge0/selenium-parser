from django.contrib import admin

from parser_app.models import ProductPhoto, Product, ProductCharacteristic

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductPhoto)
admin.site.register(ProductCharacteristic)