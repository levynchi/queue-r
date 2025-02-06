from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import JsonResponse
from .forms import RegisterForm
from .models import Profile, Order, OrderNumberTracker
import logging
import json
import requests

logger = logging.getLogger(__name__)

@login_required
def get_orders(request):
    profile = request.user.profile
    orders = Order.objects.filter(profile=profile).order_by('-timestamp')
    orders_data = [
        {
            'order_number': order.order_number,
            'timestamp': order.timestamp,
            'customer_phone_number': order.customer_phone_number,
            'status': order.status,
            'id': order.id
        }
        for order in orders
    ]
    return JsonResponse({'orders': orders_data})

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

@csrf_protect
@login_required
def send_menu(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        # Implement the logic to send the menu via WhatsApp
        # For now, we'll just log the action
        logger.debug(f"Sending menu to {phone_number}")
        return JsonResponse({'status': 'success', 'message': f'Menu sent to {phone_number}'})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_protect
@login_required
def mark_as_ready(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order_id = data.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        order.status = 'READY'
        order.save()
        logger.debug(f"Order {order_id} marked as ready")
        return JsonResponse({'status': 'success', 'message': f'Order {order_id} marked as ready'})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_protect
@login_required
def end_shift(request):
    if request.method == 'POST':
        # Reset the order numbers
        tracker, created = OrderNumberTracker.objects.get_or_create(id=1)
        tracker.reset_order_number()

        # Delete all current orders
        Order.objects.all().delete()

        return JsonResponse({'status': 'success', 'message': 'Shift ended and orders reset'})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def account_home(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    orders = Order.objects.filter(profile=profile).order_by('-timestamp')
    return render(request, 'accounts/account_home.html', {'profile': profile, 'orders': orders})

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

        try:
            profile = Profile.objects.get(twilio_phone_number=twilio_number)
            logger.debug(f"Profile found for twilio_number: {twilio_number}")

            tracker, created = OrderNumberTracker.objects.get_or_create(id=1)

            order_number = tracker.current_order_number  # Ensure this is an integer
            order = Order.objects.create(
                profile=profile,
                order_number=order_number,
                customer_phone_number=triggering_phone_number,
                status='PENDING'
            )
            logger.debug(f"Created new order: {order}")

            tracker.current_order_number += 1
            tracker.save()

        except Profile.DoesNotExist:
            logger.error(f"Profile not found for twilio_number: {twilio_number}")
            return JsonResponse({'error': 'Profile not found'}, status=404)
        return JsonResponse({'status': 'success', 'order_id': order_number})    
    logger.error("Invalid request method")
    return JsonResponse({'error': 'Invalid request method'}, status=405)
def mark_order_as_ready(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id, profile__user=request.user)
            order.status = 'READY'
            order.save()

            # Send request to Twilio function
            twilio_function_url = 'https://queue-r-django-twilio-3377.twil.io/notify_order_ready'
            payload = {
                'customer_phone_number': order.customer_phone_number,
                'order_number': order.order_number,
                'twilio_number': request.user.profile.twilio_phone_number  # Include Twilio numbe
            }
            response = requests.post(twilio_function_url, json=payload)
            response.raise_for_status()

            return JsonResponse({'status': 'success'})
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)