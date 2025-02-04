import re
from django.core.exceptions import ValidationError

def validate_international_phone_number(value):
    pattern = re.compile(r'^\+\d{1,15}$')
    if not pattern.match(value):
        raise ValidationError('Phone number must be in international format, starting with + and followed by up to 15 digits.')