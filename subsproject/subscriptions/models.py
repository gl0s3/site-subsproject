from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class Subscription(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	service_name = models.CharField(max_length=255)
	service_link = models.URLField(blank=True, null=True)
	price = models.IntegerField()
	duration = models.IntegerField()
	start_date = models.DateField(default=timezone.now)  # Убедитесь, что это DateField
	calendar_event_id = models.CharField(max_length=255, blank=True, null=True)

	def end_date(self):
		return self.start_date + timezone.timedelta(days=self.duration)

	def status(self):
		days_left = (self.end_date() - timezone.now().date()).days
		if days_left < 0:
			return "Просрочено ❌"
		else:
			return "Активна ✅"

	def clean(self):
		if self.start_date > timezone.now().date():  # Исправлено
			raise ValidationError("Дата начала не может быть в будущем")

		if self.duration > 366:
			raise ValidationError("Срок подписки не может превышать 1 год")

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class GoogleCalendarToken(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	access_token = models.CharField(max_length=255)
	refresh_token = models.CharField(max_length=255, blank=True, null=True)
	expires_at = models.DateTimeField()