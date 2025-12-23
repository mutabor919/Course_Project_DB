from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views # <-- Импортируем стандартные вьюхи
from incidents import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='incidents/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', views.register, name='register'),

    path('appeals/', views.my_appeals, name='my_appeals'),
    path('appeals/create/', views.create_appeal, name='create_appeal'),
]