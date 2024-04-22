from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
# Create your models here.


class ExtendedUser(AbstractUser):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollars'),
        ('GBP', 'British Pounds'),
        ('EUR', 'Euros'),
    ]
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00, validators=[MinValueValidator(Decimal('0.01'))])
