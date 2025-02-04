from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm 
from .models import Profile
from twilio.rest import Client  # Ensure this import is correctly placed

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('account_home')
    return render(request, 'accounts/landing_page.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('account_home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def account_home(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    return render(request, 'accounts/account_home.html', {'profile': profile})

@login_required
def send_whatsapp_message(request):
    profile = request.user.profile
    if request.method == 'POST':
        message_body = request.POST.get('message')
        client = Client(profile.twilio_sid, profile.twilio_auth_token)
        message = client.messages.create(
            body=message_body,
            from_=f'whatsapp:{profile.twilio_phone_number}',
            to=f'whatsapp:{profile.whatsapp_business_number}'
        )
        # Increment the counter
        profile.whatsapp_message_count += 1
        profile.save()
        return render(request, 'accounts/message_sent.html', {'message': message})
    return render(request, 'accounts/send_message.html')