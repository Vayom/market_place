from django.contrib import admin
from django.contrib.auth.models import User

from user_auth.models import CustomUser


admin.site.register(CustomUser)
