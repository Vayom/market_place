from django.db import models
from django.contrib.auth.models import AbstractUser

from user_auth.models import CustomUser


class Product(models.Model):
    """
    Model representing a product in the store.

    Attributes:
        name (str): The name of the product.
        description (str): The description of the product.
        price (Decimal): The price of the product.
        category (Category): The category to which the product belongs.
        user (CustomUser): The user who added the product.
    """

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class Order(models.Model):
    """
    Model representing an order in the store.

    Attributes:
        user (CustomUser): The user who placed the order.
        products (ManyToManyField): The products included in the order.
        status (str): The status of the order (e.g., "Pending", "Completed", etc.).
        total_amount (Decimal): The total amount of the order.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    status = models.CharField(max_length=50, default="Pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"



class Payment(models.Model):
    """
    Model representing a payment in the store.

    Attributes:
        order (Order): The order associated with the payment.
        payment_method (str): The payment method.
        amount_paid (Decimal): The amount paid.
    """

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)



class Category(models.Model):
    """
    Model representing a category of products.

    Attributes:
        name (str): The name of the category.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Review(models.Model):
    """
    Model representing a review for a product.

    Attributes:
        product (Product): The product being reviewed.
        user (CustomUser): The user who wrote the review.
        text (str): The text of the review.
        rating (int): The rating given in the review.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveIntegerField()

    def __str__(self):
        return f"Review {self.id} by {self.user} for product {self.product.name}"



class UserProfile(models.Model):
    """
    Model representing a user profile.

    Attributes:
        user (CustomUser): One-to-one relationship with a user (foreign key).
        address (str): User's address. Maximum length of 255 characters. Can be blank.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Cart(models.Model):
    """
    Model representing a user's shopping cart.

    Attributes:
        user (CustomUser): One-to-one relationship with a user (foreign key).
        products (ManyToManyField): A many-to-many relationship with products.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, null=True, blank=True)

    def __str__(self):
        return self.user.username


class PromoCode(models.Model):
    """
    Model representing promotional codes.

    Attributes:
        code (str): The promotional code. Maximum length of 20 characters. Unique.
        discount_amount (Decimal): The amount of discount provided by the promotional code.
    """
    code = models.CharField(max_length=20, unique=True)
    discount_amount = models.DecimalField(max_digits=5, decimal_places=2)
