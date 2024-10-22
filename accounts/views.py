from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db import IntegrityError
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
import smtplib
import ssl  # Import ssl module to use SSLContext for secure connections
from .forms import CustomUserCreationForm, CustomPasswordResetForm
from .models import UserProfile, SubscriptionPlan, UserSubscription
from django.contrib.auth.views import PasswordResetView

import smtplib
import ssl
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
import random
import string

# Function to generate a random code
def generate_random_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# View to handle the display of the form and sending the email

def send_mail_page(request):
    if request.method == 'POST':
        # Collect form data
        user_email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')

        # Generate a random code
        random_code = generate_random_code()

        # Prepare the email details
        subject = 'Trash Express Payment Confirmation and Details'
        message = f"""


        Dear {full_name},

        Thank you for providing your details. Below are your details:

        Full Name: {full_name}
        Address: {address}
        Phone Number: {phone_number}
        Email: {user_email}

        Your unique code: {random_code}

        Thank you for being with us.

        Best regards,
        Trash Express
        """
        
        # Define the recipient list, which includes the user's email and the fixed email
        recipient_list = [user_email, 'hadshtechnologies@gmail.com']

        # SMTP server details
        smtp_host = 'smtp.gmail.com'  # Replace with your SMTP host
        smtp_port = 587  # Replace with your SMTP port

        # Create an SSLContext for secure connection
        context = ssl.create_default_context()

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.ehlo()  # Identify yourself to the server
                server.starttls(context=context)  # Secure the connection using SSLContext
                server.ehlo()  # Re-identify after starting TLS
                server.login('emmasobula@gmail.com', 'hhtp rpli bqpj uxen')  # Login with your email credentials
                for recipient in recipient_list:
                    server.sendmail(
                        settings.DEFAULT_FROM_EMAIL,  # From email
                        recipient,  # To email
                        f"Subject: {subject}\n\n{message}"  # Email subject and body
                    )
                messages.success(request, 'Email sent successfully.')
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')

        return redirect('home')  # Redirect back to home after sending the email

    # Render the email form page if GET request
    return render(request, 'send_mail_page.html')



# Function to send subscription confirmation email using SSLContext
def send_subscription_email(user_email, subscription_plan_name, customer_code):
    subject = f'Your Subscription to {subscription_plan_name} on Trash Express'
    message = f'Thank you for subscribing to {subscription_plan_name}! Your customer code is {customer_code}.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email, 'hadshtechnologies@gmail.com']


    # SMTP server details
    smtp_host = 'smtp.gmail.com'  # Replace with your SMTP host
    smtp_port = 587  # Replace with your SMTP port

    # Create an SSLContext for secure connection
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()  # Identify yourself to the server
            server.starttls(context=context)  # Secure the connection using the SSLContext
            server.ehlo()  # Re-identify after starting TLS
            server.login('emmasobula@gmail.com', 'hhtp rpli bqpj uxen')  # Login with your email credentials
            server.sendmail(from_email, recipient_list, f"Subject: {subject}\n\n{message}")
            print('Subscription email sent!')
    except Exception as e:
        print(f'Failed to send email: {str(e)}')

# Homepage view
def home(request):
    return render(request, 'index.html')

# Register view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Create user and save profile information
                user = form.save(commit=False)
                user.save()

                UserProfile.objects.create(
                    user=user,
                    address=form.cleaned_data['address'],
                    phone_number=form.cleaned_data['phone_number']
                )

                # Log the user in and redirect to dashboard
                login(request, user)
                return redirect('dashboard')
            except IntegrityError:
                return HttpResponse("Username or email already exists.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

# Dashboard view (requires login)
@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    # Fetch the user's active subscriptions and update the remaining days
    user_subscriptions = UserSubscription.objects.filter(user=user)
    
    # Add remaining_days calculation for each subscription
    for subscription in user_subscriptions:
        if subscription.end_date >= today:
            subscription.remaining_days = (subscription.end_date - today).days
        else:
            subscription.remaining_days = 0
            subscription.status = 'Expired'
        subscription.save()

    return render(request, 'dashboard.html', {'user_subscriptions': user_subscriptions})

# Subscription view (requires login)
@login_required
def subscribe(request):
    user = request.user

    if request.method == 'POST':
        subscription_plan_name = request.POST.get('subscription_plan')
        try:
            # Find the selected subscription plan
            subscription_plan = SubscriptionPlan.objects.get(name=subscription_plan_name)

            # Update or create a new subscription for the user
            user_subscription, created = UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan': subscription_plan,
                    'start_date': timezone.now().date(),
                    'end_date': timezone.now().date() + timezone.timedelta(days=30),
                    'status': 'Active'
                }
            )

            # Send the subscription confirmation email
            send_subscription_email(user.email, subscription_plan.name, user_subscription.customer_code)

            messages.success(request, 'Subscription plan updated successfully!')
            return redirect('home')
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, 'Invalid subscription plan!')

    return render(request, 'subscribe.html')

# Custom Password Reset View
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'password_reset.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

# Logout view
def custom_logout(request):
    logout(request)
    return redirect(reverse('home'))

# Other simple views for rendering static pages
def payment(request):
    return render(request, 'payment.html')

def details(request):
    return render(request, 'details.html')

def pay(request):
    return render(request, 'pay.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')

def buckets(request):
    return render(request, 'buckets.html')

def carts(request):
    return render(request, 'carts.html')

def legal(request):
    return render(request, 'legal.html')
