from django.contrib import admin

from market.models import Category, Product, UserProfile, Cart, Order, Review

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(UserProfile)
admin.site.register(Order)
admin.site.register(Review)
