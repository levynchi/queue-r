from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from .validators import validate_international_phone_number

class RegisterForm(UserCreationForm):
    twilio_phone_number = forms.CharField(
        max_length=15,
        validators=[validate_international_phone_number],
        widget=forms.TextInput(attrs={'placeholder': '+1234567890'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'twilio_phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.get_or_create(user=user, defaults={'twilio_phone_number': self.cleaned_data['twilio_phone_number']})
        return user