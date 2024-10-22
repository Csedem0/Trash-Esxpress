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



@login_required
def subscribe(request):
    user = request.user
    # Check if the user already has an active subscription
    if UserSubscription.objects.filter(user=user, status='Active').exists():
        messages.warning(request, 'You already have an active subscription.')
        return redirect('dashboard')

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
                end_date=timezone.now().date() + timezone.timedelta(days=30),  # Assuming one month duration
                status='Active'  # Set status to Active
            )

            # Get the pickup code
            pickup_code = subscription.pickup_code
            
            # Prepare the email details
            subject = 'Trash Express Subscription Confirmation'
            message = f"""
            Dear {user.username},

            Thank you for subscribing to our service. Here are your subscription details:

            Subscription Plan: {subscription.plan.name}
            Start Date: {subscription.start_date}
            End Date: {subscription.end_date}
            Pickup Code: {pickup_code}

            Thank you for being with us!

            Best regards,
            Trash Express
            """

            # Define the recipient list
            recipient_list = [user.email, 'hadshtechnologies@gmail.com']

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
                    server.login('emmasobula@gmail.com', 'hhtp rpli bqpj uxen')  # Use your email credentials here
                    for recipient in recipient_list:
                        server.sendmail(
                            settings.DEFAULT_FROM_EMAIL,
                            recipient,
                            f"Subject: {subject}\n\n{message}"
                        )
                messages.success(request, 'Subscription plan updated successfully! A confirmation email has been sent.')
            except Exception as e:
                messages.error(request, f'Failed to send email: {str(e)}')
            
            return redirect('dashboard')
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, 'Invalid subscription plan!')
            return redirect('subscribe')
    else:
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
                server.login('emmasobula@gmail.com', 'hhtp rpli bqpj uxen')
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
                full_name = f"{user.first_name} {user.last_name}"
                address = form.cleaned_data['address']
                phone_number = form.cleaned_data['phone_number']

                subject = 'Welcome to Trash Express'
                message = f"""
                Hello {full_name},

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
                    server.login('emmasobula@gmail.com', 'hhtp rpli bqpj uxen')
                    for recipient in recipient_list:
                        server.sendmail(
                            'emmasobula@gmail.com',
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
