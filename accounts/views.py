from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db import IntegrityError
from django.contrib import messages
from django.conf import settings
import smtplib
import ssl  # Import ssl module to use SSLContext for secure connections
from .forms import CustomUserCreationForm, CustomPasswordResetForm
from .models import UserProfile, SubscriptionPlan, UserSubscription
from django.contrib.auth.views import PasswordResetView
import random
import string
from datetime import datetime


import ssl
import smtplib
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import random
import string

import random
import string
import ssl
import smtplib
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import UserSubscription, SubscriptionPlan, UserProfile  # Assuming these are your models
from django.conf import settings

@login_required
def subscribe(request):
    user = request.user
    active_subscription = UserSubscription.objects.filter(user=user, status='Active').first()

    if request.method == 'POST':
        subscription_plan_name = request.POST.get('subscription_plan')
        try:
            subscription_plan = SubscriptionPlan.objects.get(name=subscription_plan_name)

            # Check if the UserProfile exists for the user; if not, create one
            user_profile, created = UserProfile.objects.get_or_create(user=user)

            # Create new user subscription
            subscription = UserSubscription.objects.create(
                user=user,
                plan=subscription_plan,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=30),
                status='Active'
            )

            # Generate pickup codes
            main_pickup_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            dummy_codes = [''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) for _ in range(3)]

            # Store the pickup codes
            subscription.pickup_code = main_pickup_code
            subscription.dummy_codes = dummy_codes  # You may need to adjust this field as per your model
            subscription.save()

            # Determine pickup days based on the subscription plan
            if subscription.plan.name == "Basic":
                pickup_days_message = "Your pickup days are on Tuesdays."
            elif subscription.plan.name in ["Standard", "Premium"]:
                pickup_days_message = "Your pickup days are on Tuesdays and Fridays."
            else:
                pickup_days_message = "Your pickup days will be communicated shortly."

            # Prepare the email details for the user (no pickup codes)
            user_subject = 'Trash Express Subscription Confirmation'
            user_message = f"""
            Dear {user.username},

            Thank you for subscribing to our service. Here are your subscription details:

            Subscription Plan: {subscription.plan.name}
            Start Date: {subscription.start_date}
            End Date: {subscription.end_date}
            {pickup_days_message}

            To view your pickup code, please visit your dashboard: https://trash-esxpress.onrender.com/accounts/dashboard

            Thank you for being with us!

            Best regards,
            Trash Express
            """

            # Prepare the email details for hadshtechnologies@gmail.com (with all codes)
            admin_subject = 'New Subscription Confirmation - Trash Express'
            admin_message = f"""
            A new subscription has been created.

            User: {user.username}
            Subscription Plan: {subscription.plan.name}
            Start Date: {subscription.start_date}
            End Date: {subscription.end_date}
            Main Pickup Code: {main_pickup_code}
            Other Pickup Codes: {', '.join(dummy_codes)}

            Best regards,
            Trash Express
            """

            # Define the recipient list
            recipient_list = [user.email, 'hadshtechnologies@gmail.com']

            # SMTP server details
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587

            context = ssl.create_default_context()

            try:
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login('hadshtechnologies@gmail.com', 'wuwv mhdx qxte tymm')  # Use your email credentials here
                    
                    # Send email to the user (without pickup codes)
                    server.sendmail(
                        settings.DEFAULT_FROM_EMAIL,
                        user.email,
                        f"Subject: {user_subject}\n\n{user_message}"
                    )

                    # Send email to admin (with all pickup codes)
                    server.sendmail(
                        settings.DEFAULT_FROM_EMAIL,
                        'hadshtechnologies@gmail.com',
                        f"Subject: {admin_subject}\n\n{admin_message}"
                    )

                messages.success(request, 'Subscription plan updated successfully! A confirmation email has been sent.')
            except Exception as e:
                messages.error(request, f'Failed to send email: {str(e)}')
            
            return redirect('dashboard')
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, 'Invalid subscription plan!')
            return redirect('subscribe')
    else:
        if active_subscription:
            messages.info(request, 'You currently have an active subscription. You can subscribe again if you wish to change your plan.')

        return render(request, 'subscribe.html')




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

        # Get the current day of the week (0=Monday, 6=Sunday)
        current_day = datetime.today().weekday()

        # Determine pickup day message
        if current_day in [0, 1, 2, 3]:  # Monday (0), Tuesday (1), Wednesday (2), Thursday (3)
            pickup_day_message = "Your pick up day will be on Friday."
        else:  # Friday (4), Saturday (5), Sunday (6)
            pickup_day_message = "Your pick up day will be on Tuesday."

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

        {pickup_day_message}

        Thank you for being with us.

        Best regards,
        Trash Express
        """

        # Define the recipient list, which includes the user's email and a fixed email
        recipient_list = [user_email, 'hadshtechnologies@gmail.com']

        # SMTP server details
        smtp_host = 'smtp.gmail.com'
        smtp_port = 587

        # Create an SSLContext for secure connection
        context = ssl.create_default_context()

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login('hadshtechnologies@gmail.com', 'wuwv mhdx qxte tymm') 
                for recipient in recipient_list:
                    server.sendmail(
                        settings.DEFAULT_FROM_EMAIL,
                        recipient,
                        f"Subject: {subject}\n\n{message}"
                    )
                messages.success(request, 'Email sent successfully.')
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')

        return redirect('home')

    return render(request, 'send_mail_page.html')






# Homepage view
def home(request):
    return render(request, 'index.html')


# Register view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.save()

                UserProfile.objects.create(
                    user=user,
                    address=form.cleaned_data['address'],
                    phone_number=form.cleaned_data['phone_number']
                )

                login(request, user)

                user_email = user.email
                user_name = f"{user.username}"
                address = form.cleaned_data['address']
                phone_number = form.cleaned_data['phone_number']

                subject = 'Welcome to Trash Express'
                message = f"""
                Hello {user_name},

                Thank you for registering with Trash Express. Below are your details:

                Address: {address}
                Phone Number: {phone_number}
                Email: {user_email}

                Best regards,
                Trash Express
                """

                recipient_list = [user_email, 'hadshtechnologies@gmail.com']

                smtp_host = 'smtp.gmail.com'
                smtp_port = 587
                context = ssl.create_default_context()

                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login('hadshtechnologies@gmail.com', 'wuwv mhdx qxte tymm') 
                    for recipient in recipient_list:
                        server.sendmail(
                            'hadshtechnologies@gmail.com',
                            recipient,
                            f"Subject: {subject}\n\n{message}"
                        )

                messages.success(request, 'Registration successful and email sent.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Error during registration: {str(e)}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


# Dashboard view (requires login)
@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    user_subscriptions = UserSubscription.objects.filter(user=user)

    for subscription in user_subscriptions:
        if subscription.end_date >= today:
            subscription.remaining_days = (subscription.end_date - today).days
        else:
            subscription.remaining_days = 0
            subscription.status = 'Expired'

        # Check if dummy codes should be displayed based on the date
        days_since_subscription = (today - subscription.start_date).days
        if days_since_subscription < 7:
            subscription.dummy_code_to_show = None  # Show no dummy codes yet
        elif days_since_subscription < 14:
            subscription.dummy_code_to_show = subscription.dummy_codes[0]  # Show the first dummy code
        elif days_since_subscription < 21:
            subscription.dummy_code_to_show = subscription.dummy_codes[1]  # Show the second dummy code
        elif days_since_subscription < 28:
            subscription.dummy_code_to_show = subscription.dummy_codes[2]  # Show the third dummy code
        else:
            subscription.dummy_code_to_show = None  # No dummy codes to show after 28 days
        
        subscription.save()

    return render(request, 'dashboard.html', {'user_subscriptions': user_subscriptions})






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


# Payment view (requires login)
@login_required
def payment(request):
    user = request.user
    today = timezone.now().date()

    try:
        user_subscription = UserSubscription.objects.filter(user=user, status='Active', end_date__gte=today).first()

        if user_subscription:
            messages.error(request, 'You already have an active subscription.')
            return redirect('dashboard')

    except UserSubscription.DoesNotExist:
        pass

    return render(request, 'payment.html')



def collector_pickup(request):
    if request.method == 'POST':
        # Collect form data
        collector_email = request.POST.get('email')
        pickup_code = request.POST.get('pickup_code')

        # Validate email format
        try:
            validate_email(collector_email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'collector_pickup_form.html')

        # Prepare the email details
        subject = 'Trash Express Pickup Code Confirmation'
        message = f"""
        Dear Waste Collector,

        Please note: Below is the pickup code you submitted, ensure it is accurate because wrong pickup code leads to no pay for that pickup!

        Pickup Code: {pickup_code}

        Thank you for your service.

        Best regards,
        Trash Express
        """

        # Admin email message
        admin_message = f"""
        A waste collector has submitted a pickup code.

        Email: {collector_email}
        Pickup Code: {pickup_code}

        Best regards,
        Trash Express
        """

        # Define the recipient list
        recipient_list = [collector_email, 'hadshtechnologies@gmail.com']

        # SMTP server details
        smtp_host = 'smtp.gmail.com'
        smtp_port = 587

        # Create an SSLContext for secure connection
        context = ssl.create_default_context()

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login('hadshtechnologies@gmail.com', 'wuwv mhdx qxte tymm')  # Use your email credentials here

                # Send email to the waste collector
                server.sendmail(
                    settings.DEFAULT_FROM_EMAIL,
                    collector_email,
                    f"Subject: {subject}\n\n{message}"
                )

                # Send email to the admin
                server.sendmail(
                    settings.DEFAULT_FROM_EMAIL,
                    'hadshtechnologies@gmail.com',
                    f"Subject: {subject}\n\n{admin_message}"
                )

            messages.success(request, 'Pickup code sent successfully.')
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')

        return redirect('collector_pickup')  # Redirect back to the form after submission

    return render(request, 'collector_pickup_form.html')







# Other views for static pages
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
