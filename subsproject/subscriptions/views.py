from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, SubscriptionForm
from .models import Subscription, GoogleCalendarToken


def home(request):
	return render(request, 'subscriptions/home.html')


def signup(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			messages.success(request, 'Регистрация прошла успешно!')
			return redirect('login')
		else:
			for field, errors in form.errors.items():
				for error in errors:
					messages.error(request, f"{error}")
	else:
		form = SignUpForm()
	return render(request, 'subscriptions/signup.html', {'form': form})


def login_view(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('dashboard')
		else:
			messages.error(request, 'Неверный логин или пароль')
	return render(request, 'subscriptions/login.html')


@login_required
def dashboard(request):
	subscriptions = Subscription.objects.filter(user=request.user)
	total_spent = sum(sub.price for sub in subscriptions)
	active_subs = sum(1 for sub in subscriptions if sub.status() == "Активна ✅")
	has_calendar_token = GoogleCalendarToken.objects.filter(user=request.user).exists()

	return render(request, 'subscriptions/dashboard.html', {
		'subscriptions': subscriptions,
		'total_spent': total_spent,
		'active_subs': active_subs,
		'has_calendar_token': has_calendar_token
	})

def confirmation_success(request):
	return render(request, 'subscriptions/confirmation_success.html')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SubscriptionForm
from .models import Subscription

@login_required
def add_subscription(request):
    if request.user.is_authenticated:
        return redirect('home')  # Перенаправляем на главную страницу
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            messages.success(request, 'Подписка успешно добавлена!')
            return redirect('dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = SubscriptionForm()
    return render(request, 'subscriptions/add_subscription.html', {'form': form})