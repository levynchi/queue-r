from django.urls import path
from . import views
from django.urls import include

urlpatterns = [
    path('', views.landing_page, name='landing_page'),  # Landing page
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('account_home/', views.account_home, name='account_home'),
    path('whatsapp/incoming/', views.incoming_whatsapp_message, name='incoming_whatsapp_message'),
    path('send_menu/', views.send_menu, name='send_menu'),
    path('mark_as_ready/', views.mark_as_ready, name='mark_as_ready'),
    path('end_shift/', views.end_shift, name='end_shift'),
    path('end_shift/', views.end_shift, name='end_shift'),
    path('get_orders/', views.get_orders, name='get_orders'),
    path('mark_order_as_ready/<int:order_id>/', views.mark_order_as_ready, name='mark_order_as_ready'),
    path('logout/', views.custom_logout, name='logout'), # Custom logout view
]