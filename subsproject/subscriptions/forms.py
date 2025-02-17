from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Subscription

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже зарегистрирован")
        return email

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['service_name', 'service_link', 'price', 'duration', 'start_date']
        widgets = {
            'service_link': forms.URLInput(attrs={'placeholder': 'example.com'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError("Цена должна быть больше нуля")
        return price

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration < 1:
            raise ValidationError("Срок должен быть не менее 1 дня")
        return duration

    def clean_service_link(self):
        service_link = self.cleaned_data.get('service_link')
        if service_link and not service_link.startswith(('http://', 'https://')):
            service_link = 'http://' + service_link
        return service_link
