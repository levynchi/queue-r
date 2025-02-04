from django.shortcuts import redirect
from django.urls import reverse
# Middleware to ensure authenticated users have a twilio_phone_number set, redirecting them to update_phone_number if not.
class CheckPhoneNumberMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = request.user.profile
            if not profile.twilio_phone_number:
                if request.path != reverse('update_phone_number'):
                    return redirect('update_phone_number')
        response = self.get_response(request)
        return response