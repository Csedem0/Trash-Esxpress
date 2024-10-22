import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

def generate_unique_code():
    return str(uuid.uuid4())[:8].upper()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_months = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, default='Active')  # Active, Expired, etc.
    customer_code = models.CharField(max_length=10, unique=True, editable=False, default='SUB_DEFAULT')
    pickup_code = models.CharField(max_length=10, unique=True, editable=False, default='PICKUP_DEFAULT')

    def save(self, *args, **kwargs):
        if not self.customer_code or self.customer_code == 'SUB_DEFAULT':
            self.customer_code = generate_unique_code()

        # Ensure that pickup_code is unique, if not already generated
        if not self.pickup_code or self.pickup_code == 'PICKUP_DEFAULT':
            self.pickup_code = generate_unique_code()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Subscription to {self.plan.name}"

