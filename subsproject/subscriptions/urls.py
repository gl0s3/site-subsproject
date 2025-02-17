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
    path('delete_subscription/<int:subscription_id>/', views.delete_subscription, name='delete_subscription'),
    path('toggle_theme/', views.toggle_theme, name='toggle_theme'),
]
