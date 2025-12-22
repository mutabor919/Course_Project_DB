from django.contrib import admin
from .models import (
    Role, Department, CustomUser, Category, Priority, Status,
    Appeal, Assignment, ActionLog, BackupLog, Report, Comment
)

# Регистрация моделей в админке
admin.site.register(Role)
admin.site.register(Department)
admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Priority)
admin.site.register(Status)
admin.site.register(Appeal)
admin.site.register(Assignment)
admin.site.register(ActionLog)
admin.site.register(BackupLog)
admin.site.register(Report)
admin.site.register(Comment)