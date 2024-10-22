from django.core.mail import send_mail

def send_subscription_email(user_email, plan_name, customer_code):
    send_mail(
        'Subscription Successful!',
        f'Your subscription to {plan_name} has been activated. Your customer code is {customer_code}.',
        'from@example.com',
        [user_email],
        fail_silently=False,
    )
