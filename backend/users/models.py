from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class User(User):
    phone_number = models.CharField('Phone number', max_length=9, unique=True)
