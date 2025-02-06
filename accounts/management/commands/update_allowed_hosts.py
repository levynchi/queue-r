import requests
from django.core.management.base import BaseCommand
from pathlib import Path
import re

class Command(BaseCommand):
    help = 'Update ALLOWED_HOSTS with the current ngrok URL'

    def handle(self, *args, **kwargs):
        try:
            # Fetch the current ngrok URL
            response = requests.get('http://127.0.0.1:4040/api/tunnels')
            data = response.json()
            ngrok_url = data['tunnels'][0]['public_url'].replace('https://', '').replace('http://', '')

            # Update ALLOWED_HOSTS in settings.py
            settings_path = Path(__file__).resolve().parent.parent.parent.parent / 'queueR' / 'settings.py'
            
            # Print the settings_path
            self.stdout.write(self.style.SUCCESS(f'settings_path: {settings_path}'))

            with open(settings_path, 'r') as file:
                settings_content = file.read()

            # Use regex to replace the ALLOWED_HOSTS line
            new_allowed_hosts = f"ALLOWED_HOSTS = ['localhost', '127.0.0.1', '{ngrok_url}']"
            settings_content = re.sub(r"ALLOWED_HOSTS = \[.*?\]", new_allowed_hosts, settings_content, flags=re.DOTALL)

            with open(settings_path, 'w') as file:
                file.write(settings_content)

            self.stdout.write(self.style.SUCCESS(f'Successfully updated ALLOWED_HOSTS with {ngrok_url}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating ALLOWED_HOSTS: {e}'))