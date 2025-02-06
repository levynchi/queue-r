@echo off

:: Navigate to the project directory
cd /d "C:\Users\levyn\OneDrive\שולחן העבודה\queue-r"

:: Start Django server
start "" python manage.py runserver

:: Wait for the Django server to start
timeout /t 5 /nobreak

:: Start ngrok
start "" ngrok http 8000

:: Wait for ngrok to start
timeout /t 5 /nobreak

:: Update ALLOWED_HOSTS
python manage.py update_allowed_hosts