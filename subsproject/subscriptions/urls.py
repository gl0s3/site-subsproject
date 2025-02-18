from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_subscription/', views.add_subscription, name='add_subscription'),
    path('edit_subscription/<int:subscription_id>/', views.edit_subscription, name='edit_subscription'),
    path('renew_subscription/<int:subscription_id>/', views.renew_subscription, name='renew_subscription'),
    path('delete_subscription/<int:subscription_id>/', views.delete_subscription, name='delete_subscription'),
    path('share_subscription/<int:subscription_id>/', views.share_subscription, name='share_subscription'),
    path('join_subscription/', views.join_subscription, name='join_subscription'),
    path('statistics/', views.statistics, name='statistics'),
    path('recovery/', views.recovery, name='recovery'),
    path('toggle_theme/', views.toggle_theme, name='toggle_theme'),
]