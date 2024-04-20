from django.db import models
from django.contrib.auth.models import AbstractUser

from user_auth.models import CustomUser


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    # Добавьте другие поля, такие как изображения и количество на складе, по вашему усмотрению

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    status = models.CharField(max_length=50, default="Pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Другие поля, такие как дата и время заказа, могут быть добавлены по вашему усмотрению

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    # Другие поля, связанные с платежами, могут быть добавлены по вашему усмотрению


class Category(models.Model):
    name = models.CharField(max_length=100)

    # Другие поля, связанные с категориями товаров, могут быть добавлены по вашему усмотрению

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveIntegerField()

    def __str__(self):
        return f"Review {self.id} by {self.user} for product {self.product.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, null=True, blank=True)

    def __str__(self):
        return self.user.username


class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_amount = models.DecimalField(max_digits=5, decimal_places=2)
    # Другие поля, связанные с промокодами, могут быть добавлены по вашему усмотрению
