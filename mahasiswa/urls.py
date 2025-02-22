from django.urls import path
from . import views

urlpatterns = [
    path('',views.login, name="login"),
    path('register/',views.register, name="register"),
    path('dashboard/',views.dashboard, name="dashboard"),
    path('dashboard/filter/',views.filter, name="filter"),
    path('dashboard/grafik/',views.grafik, name="grafik"),
    path('dashboard/profile/',views.profile, name="profile"),
    path('dashboard/input/',views.input, name="input"),
    path('dashboard/schedule/',views.schedule, name="schedule"),
    path('dashboard/attendance/',views.attendance, name="attendance"),
    path('input_data/',views.input_data, name="input_data"),
    path('logout/', views.logout, name='logout'),
    path('update/<str:nim>/', views.update, name='update'),
    path('update_profile/<str:nim>/', views.update_profile, name='update_profile'),
    path('delete/<str:nim>/', views.delete, name='delete'),
    path('edit/<str:nim>/', views.edit, name='edit'),
]