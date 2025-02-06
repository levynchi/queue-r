from django.db import models
from django.contrib.auth.models import User
from .validators import validate_international_phone_number
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    twilio_phone_number = models.CharField(max_length=15, blank=True, validators=[validate_international_phone_number])
    whatsapp_message_count = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('READY', 'Ready'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    order_number = models.IntegerField(unique=True)
    timestamp = models.DateTimeField(default=timezone.now)
    customer_phone_number = models.CharField(max_length=15, validators=[validate_international_phone_number])
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Order #{self.order_number} - {self.status}"
class OrderNumberTracker(models.Model):
    current_order_number = models.IntegerField(default=50)

    def reset_order_number(self):
            self.current_order_number = 50
            self.save()