from django.db import models
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings


# Create your models here.
class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('SEND', 'Send Money'),
        ('REQUEST', 'Request Money'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_transactions', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_transactions', on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=[('USD', 'US Dollars'), ('GBP', 'British Pounds'), ('EUR', 'Euros')])
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)
    is_notified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.amount} {self.currency} [{self.status}]"

    class Meta:
        ordering = ['-created_at']  # Orders by `created_at` in descending order


