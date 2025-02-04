from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import RegisterForm
from .models import Profile
import logging
import json

logger = logging.getLogger(__name__)

def landing_page(request):
    logger.debug("Landing page accessed")
    if request.user.is_authenticated:
        logger.debug(f"User {request.user.username} is authenticated, redirecting to account_home")
        return redirect('account_home')
    logger.debug("User is not authenticated, rendering landing_page.html")
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

@csrf_exempt
def incoming_whatsapp_message(request):
    if request.method == 'POST':
        logger.debug(f"Received POST request with body: {request.body}")

        try:
            data = json.loads(request.body)
            triggering_phone_number = data.get('triggering_phone_number')
            message_body = data.get('message_body')
            twilio_number = data.get('twilio_number')
        except json.JSONDecodeError:
            logger.error("Invalid JSON")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        logger.debug(f"Extracted triggering_phone_number: {triggering_phone_number}, message_body: {message_body}, twilio_number: {twilio_number}")

        if not triggering_phone_number or not message_body or not twilio_number:
            logger.error("Missing triggering_phone_number, message_body, or twilio_number")
            return JsonResponse({'error': 'Missing triggering_phone_number, message_body, or twilio_number'}, status=400)

        # Find the profile associated with the Twilio number
# Find the profile associated with the Twilio number
        try:
            profile = Profile.objects.get(twilio_phone_number=twilio_number)
            logger.debug(f"Profile found for twilio_number: {twilio_number}")
            
            # Increment the counter
            logger.debug(f"Current whatsapp_message_count: {profile.whatsapp_message_count}")
            profile.whatsapp_message_count += 1
            profile.save()
            logger.debug(f"Updated whatsapp_message_count: {profile.whatsapp_message_count}")
        except Profile.DoesNotExist:
            logger.error(f"Profile not found for twilio_number: {twilio_number}")
            return JsonResponse({'error': 'Profile not found'}, status=404)
        return JsonResponse({'status': 'success'})
    logger.error("Invalid request method")
    return JsonResponse({'error': 'Invalid request method'}, status=405)