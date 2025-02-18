from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import uuid


class Subscription(models.Model):
    DURATION_CHOICES = [
        (30, '1 месяц'),
        (90, '3 месяца'),
        (180, '6 месяцев'),
        (365, '1 год'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=255)
    service_link = models.URLField(blank=True, null=True)
    price = models.IntegerField()
    duration = models.IntegerField(choices=DURATION_CHOICES, default=30)
    start_date = models.DateField(default=timezone.now)
    calendar_event_id = models.CharField(max_length=255, blank=True, null=True)
    share_code = models.CharField(max_length=255, blank=True, null=True)
    shared_with = models.ManyToManyField(User, related_name='shared_subscriptions', blank=True)

    def end_date(self):
        return self.start_date + timezone.timedelta(days=self.duration)

    def status(self):
        days_left = (self.end_date() - timezone.now().date()).days
        if days_left < 0:
            return "Просрочено ❌"
        elif days_left == 0:
            return "Истекает сегодня ⚠️"
        else:
            return f"Активна ✅ (осталось {days_left} дней)"

    def clean(self):
        if self.start_date > timezone.now().date():
            raise ValidationError("Дата начала не может быть в будущем")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        # Отправка уведомления, если до окончания подписки осталось 3 дня
        days_left = (self.end_date() - timezone.now().date()).days
        if days_left == 3:
            send_mail(
                'Ваша подписка скоро истекает',
                f'Подписка на {self.service_name} истекает через 3 дня.',
                settings.DEFAULT_FROM_EMAIL,
                [self.user.email],
                fail_silently=False,
            )

    def __str__(self):
        return self.service_name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=10, choices=[('light', 'Светлая'), ('dark', 'Темная')], default='light')
    recovery_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Профиль {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        UserProfile.objects.create(user=instance)