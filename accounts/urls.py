# urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from .views import custom_logout, CustomPasswordResetView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('details/', views.details, name='details'),
    path('pay/', views.pay, name='pay'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('buckets/', views.buckets, name='buckets'),
    path('carts/', views.carts, name='carts'),
    path('legal/', views.legal, name='legal'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    # path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Add this line
    path('subscribe/', views.subscribe, name='subscribe'),  # Add this line
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_form.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    # Add other URLs as needed
    path('send_mail_page/', views.send_mail_page, name='send_mail_page'),
    path('payment/', views.payment, name='payment')
]
