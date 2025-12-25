from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from incidents import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='incidents/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', views.register, name='register'),

    path('appeals/', views.my_appeals, name='my_appeals'),
    path('appeals/create/', views.create_appeal, name='create_appeal'),
    path('appeals/<int:pk>/', views.appeal_detail, name='appeal_detail'),

    path('export/csv/', views.export_appeals_csv, name='export_csv'),
    path('export/json/', views.export_appeals_json, name='export_json'),
    path('export/pdf/', views.export_appeals_pdf, name='export_pdf'),

    path('backup/create/', views.trigger_backup, name='trigger_backup'),

    path('appeals/<int:pk>/take/', views.take_appeal, name='take_appeal'),
    path('appeals/<int:pk>/close/', views.close_appeal, name='close_appeal'),

    path('reports/history/', views.report_history, name='report_history'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)