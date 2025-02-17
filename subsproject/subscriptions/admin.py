from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_name', 'price', 'duration', 'start_date', 'status')
    list_filter = ('user', 'start_date')
    search_fields = ('service_name', 'user__username')

