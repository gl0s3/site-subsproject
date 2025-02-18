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


class ShareForm(forms.ModelForm):
    share_code = forms.CharField(label='Код для совместного доступа', max_length=255, required=True)

    class Meta:
        model = Subscription
        fields = ['share_code']


class RenewSubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['duration']


class RecoveryForm(forms.Form):
    email = forms.EmailField(label='Email для восстановления')