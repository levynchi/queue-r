from django.db import models
from django.contrib.auth.models import User
from .validators import validate_international_phone_number

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    twilio_phone_number = models.CharField(max_length=15, blank=True, validators=[validate_international_phone_number])
    whatsapp_message_count = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username