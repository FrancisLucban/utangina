from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('debt/add/', views.debt_create, name='debt_create'),
    path('debt/<uuid:pk>/', views.debt_detail, name='debt_detail'),
    path('debt/<uuid:pk>/edit/', views.debt_edit, name='debt_edit'),
    path('debt/<uuid:pk>/delete/', views.debt_delete, name='debt_delete'),
]