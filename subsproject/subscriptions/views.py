from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import SignUpForm, SubscriptionForm, ShareForm, RecoveryForm, RenewSubscriptionForm
from .models import Subscription, UserProfile
from datetime import timedelta
from django.utils import timezone
import uuid
import json
from collections import defaultdict


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
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
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()
    return render(request, 'subscriptions/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверный логин или пароль. Если у вас нет аккаунта, зарегистрируйтесь.')
            return redirect('signup')
    return render(request, 'subscriptions/login.html')


@login_required
def dashboard(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    shared_subscriptions = Subscription.objects.filter(shared_with=request.user)
    total_spent = sum(sub.price for sub in subscriptions)
    active_subs = sum(1 for sub in subscriptions if "Активна" in sub.status())

    return render(request, 'subscriptions/dashboard.html', {
        'subscriptions': subscriptions,
        'shared_subscriptions': shared_subscriptions,
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
def edit_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=subscription)
        if form.is_valid():
            form.save()
            messages.success(request, 'Подписка успешно обновлена!')
            return redirect('dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = SubscriptionForm(instance=subscription)
    return render(request, 'subscriptions/edit_subscription.html', {'form': form})

@login_required
def renew_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    if request.method == 'POST':
        form = RenewSubscriptionForm(request.POST, instance=subscription)
        if form.is_valid():
            subscription.start_date = timezone.now().date()
            subscription.save()
            messages.success(request, 'Подписка успешно продлена!')
            return redirect('dashboard')
    else:
        form = RenewSubscriptionForm(instance=subscription)
    return render(request, 'subscriptions/renew_subscription.html', {'form': form})

@login_required
def delete_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    subscription.delete()
    messages.success(request, 'Подписка успешно удалена!')
    return redirect('dashboard')


@login_required
def share_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    if request.method == 'POST':
        form = ShareForm(request.POST, instance=subscription)
        if form.is_valid():
            subscription.share_code = str(uuid.uuid4())[:8]  # Генерация уникального кода
            subscription.save()
            messages.success(request, 'Подписка успешно поделена!')
            return redirect('dashboard')
    else:
        form = ShareForm(instance=subscription)
    return render(request, 'subscriptions/share_subscription.html', {'form': form})


@login_required
def join_subscription(request):
    if request.method == 'POST':
        share_code = request.POST.get('share_code')
        try:
            subscription = Subscription.objects.get(share_code=share_code)
            subscription.shared_with.add(request.user)
            messages.success(request, 'Вы успешно присоединились к подписке!')
        except Subscription.DoesNotExist:
            messages.error(request, 'Неверный код подписки.')
    return redirect('dashboard')


@login_required
def statistics(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    shared_subscriptions = Subscription.objects.filter(shared_with=request.user)

    # Объединяем подписки пользователя и поделенные подписки
    all_subscriptions = list(subscriptions) + list(shared_subscriptions)

    # Статистика по месяцам
    monthly_spending = defaultdict(float)
    current_year = timezone.now().year
    current_month = timezone.now().month

    for sub in all_subscriptions:
        if sub.status() == "Просрочено ❌":
            continue  # Пропускаем просроченные подписки

        # Рассчитываем месяцы, в которые действует подписка
        start_date = sub.start_date
        end_date = sub.end_date()

        # Разделяем стоимость подписки между всеми участниками
        total_users = 1 + sub.shared_with.count()
        price_per_user = sub.price / total_users

        # Если подписка на 6 месяцев или год, учитываем только месяц оплаты
        if sub.duration in [180, 365]:  # 6 месяцев или год
            month_start = start_date.replace(day=1)
            monthly_spending[month_start.month] += price_per_user
        else:
            # Для других подписок распределяем стоимость по месяцам
            for month in range(1, 13):
                month_start = timezone.datetime(current_year, month, 1).date()
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

                # Если подписка активна в этом месяце
                if start_date <= month_end and end_date >= month_start:
                    monthly_spending[month] += price_per_user

    # Преобразуем данные для диаграммы
    months = [timezone.datetime(current_year, month, 1).strftime('%B') for month in range(1, 13)]
    amounts = [monthly_spending[month] for month in range(1, 13)]

    # Цвета для месяцев
    colors = []
    for month in range(1, 13):
        if month < current_month:
            colors.append('rgba(255, 99, 132, 0.5)')  # Прошедшие месяцы (красный)
        elif month == current_month:
            colors.append('rgba(255, 206, 86, 0.5)')  # Текущий месяц (желтый)
        else:
            colors.append('rgba(75, 192, 192, 0.5)')  # Будущие месяцы (зеленый)

    return render(request, 'subscriptions/statistics.html', {
        'months': json.dumps(months),
        'amounts': json.dumps(amounts),
        'colors': json.dumps(colors),
    })

def recovery(request):
    if request.method == 'POST':
        form = RecoveryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                profile = UserProfile.objects.get(recovery_email=email)
                send_mail(
                    'Восстановление аккаунта',
                    f'Ваш логин: {profile.user.username}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Инструкции по восстановлению отправлены на ваш email.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден.')
    else:
        form = RecoveryForm()
    return render(request, 'subscriptions/recovery.html', {'form': form})


def toggle_theme(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            if profile.theme == 'dark':
                profile.theme = 'light'
            else:
                profile.theme = 'dark'
            profile.save()
        else:
            theme = request.session.get('theme', 'light')
            request.session['theme'] = 'dark' if theme == 'light' else 'light'
    return redirect(request.META.get('HTTP_REFERER', 'home'))