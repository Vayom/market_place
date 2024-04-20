from django.db.models.signals import post_save
from django.dispatch import receiver
from user_auth.models import CustomUser
from .models import Cart, UserProfile


@receiver(post_save, sender=CustomUser)
def create_user_cart_and_profile(sender, instance, created, **kwargs):
    if created:
        # Создание корзины для нового пользователя
        Cart.objects.create(user=instance)
        # Создание профиля пользователя
        UserProfile.objects.create(user=instance)
