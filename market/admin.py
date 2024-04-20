from django.contrib import admin

from market.models import Category, Product, UserProfile, Cart, Order

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(UserProfile)
admin.site.register(Order)
