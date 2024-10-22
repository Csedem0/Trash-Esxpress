from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import SubscriptionPlan

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

class CustomUserCreationForm(UserCreationForm):
    address = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'address', 'phone_number']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already taken.")
        return username

class SubscriptionForm(forms.Form):
    plan = forms.ModelChoiceField(queryset=SubscriptionPlan.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
