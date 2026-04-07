from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
