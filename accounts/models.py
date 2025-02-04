from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    whatsapp_business_number = models.CharField(max_length=15, blank=True)
    twilio_sid = models.CharField(max_length=64, blank=True)
    twilio_auth_token = models.CharField(max_length=64, blank=True)
    twilio_phone_number = models.CharField(max_length=15, blank=True)
    whatsapp_message_count = models.IntegerField(default=0)


    def __str__(self):
        return self.user.username
