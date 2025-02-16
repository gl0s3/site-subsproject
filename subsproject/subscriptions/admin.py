from django.contrib import admin
from .models import Subscription, GoogleCalendarToken

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_name', 'price', 'duration', 'start_date', 'status')
    list_filter = ('user', 'start_date')
    search_fields = ('service_name', 'user__username')

@admin.register(GoogleCalendarToken)
class GoogleCalendarTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'expires_at')
    search_fields = ('user__username',)