from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, SubscriptionForm
from .models import Subscription, UserProfile

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
    active_subs = sum(1 for sub in subscriptions if "Активна" in sub.status())

    return render(request, 'subscriptions/dashboard.html', {
        'subscriptions': subscriptions,
        'total_spent': total_spent,
        'active_subs': active_subs,
    })

@login_required
def add_subscription(request):
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

@login_required
def delete_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    subscription.delete()
    messages.success(request, 'Подписка успешно удалена!')
    return redirect('dashboard')

def toggle_theme(request):
    if request.method == 'POST':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if profile.theme == 'dark':
            profile.theme = 'light'
        else:
            profile.theme = 'dark'
        profile.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))
