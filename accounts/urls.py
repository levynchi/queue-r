from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),  # Landing page
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('account_home/', views.account_home, name='account_home'),
]