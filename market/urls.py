from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from market import views
from market.views import ProductRetrieveUpdateDestroyViewSet

app_name = 'market'

router = routers.DefaultRouter()
router.register(r'my_products', ProductRetrieveUpdateDestroyViewSet, basename='my_products')

urlpatterns = [
    path('products/', views.ProductListCreate.as_view(), name='products'),
    path('product_detail/<int:pk>/', views.ProductDetail.as_view(), name='product_detail'),
    path('product_to_cart/<int:product_id>/', views.AddProductToCart.as_view(), name='product_to_cart'),

    path('cart/', views.CartDetail.as_view(), name='cart'),

    path('order_create/', views.CreateOrderFromCart.as_view(), name='order_create'),
    path('order_cancel/<int:order_id>', views.CancelOrder.as_view(), name='order_cancel'),

    path('create_review/<int:product_id>', views.CreateReviewView.as_view(), name='create_review'),
    path('delete_review/<int:review_id>', views.DeleteReviewView.as_view(), name='delete_review'),

    path('', include(router.urls), name='my_products'),
]
