from django.db import models
from django.contrib.auth.models import AbstractUser


# 1. Роль (Role)
class Role(models.Model):
    name = models.CharField("Наименование роли", max_length=100)
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"


# 2. Отдел (Department)
class Department(models.Model):
    name = models.CharField("Наименование отдела", max_length=100)
    description = models.TextField("Описание", blank=True)
    head = models.CharField("Руководитель", max_length=100, blank=True)
    phone = models.CharField("Контактный телефон", max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"


# 3. Пользователь (CustomUser)
class CustomUser(AbstractUser):
    fio = models.CharField("ФИО", max_length=255)
    phone = models.CharField("Телефон", max_length=20, blank=True)

    # Связи
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Отдел")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Роль")

    def __str__(self):
        return f"{self.username} ({self.fio})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


# 4. Категория (Category)
class Category(models.Model):
    name = models.CharField("Наименование категории", max_length=100)
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


# 5. Приоритет (Priority)
class Priority(models.Model):
    level = models.CharField("Уровень приоритета", max_length=50)
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return self.level

    class Meta:
        verbose_name = "Приоритет"
        verbose_name_plural = "Приоритеты"


# 6. Статус (Status)
class Status(models.Model):
    name = models.CharField("Наименование статуса", max_length=50)
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"


# 7. Обращение (Appeal)
class Appeal(models.Model):
    topic = models.CharField("Тема", max_length=200)
    description = models.TextField("Описание проблемы")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    closed_at = models.DateTimeField("Дата закрытия", null=True, blank=True)

    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='my_appeals',
                                  verbose_name="Заявитель")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Категория")
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, verbose_name="Приоритет")
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, verbose_name="Статус")

    def __str__(self):
        return f"Обращение #{self.id}: {self.topic}"

    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"


# 8. Назначение (Assignment)
class Assignment(models.Model):
    appeal = models.ForeignKey(Appeal, on_delete=models.CASCADE, related_name='assignments', verbose_name="Обращение")
    performer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Сотрудник ИБ")
    assigned_at = models.DateTimeField("Дата назначения", auto_now_add=True)
    comment = models.TextField("Комментарий к назначению", blank=True)

    class Meta:
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"


# 9. Журнал действий (ActionLog)
class ActionLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name="Пользователь")
    appeal = models.ForeignKey(Appeal, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Обращение")
    action_type = models.CharField("Тип действия", max_length=100)
    description = models.TextField("Комментарий/Описание", blank=True)
    timestamp = models.DateTimeField("Дата и время", auto_now_add=True)

    class Meta:
        verbose_name = "Журнал действий"
        verbose_name_plural = "Журнал действий"


# 10. Резервная копия (BackupLog)
class BackupLog(models.Model):
    initiator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name="Пользователь")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    file_name = models.CharField("Имя файла", max_length=255)
    status = models.CharField("Статус копирования", max_length=50)
    file_path = models.CharField("Путь к копии", max_length=500)

    class Meta:
        verbose_name = "Резервная копия"
        verbose_name_plural = "Резервные копии"


# 11. Отчет (Report)
class Report(models.Model):
    initiator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    report_type = models.CharField("Тип отчета", max_length=50)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    appeal_count = models.IntegerField("Количество обращений", default=0)
    file_path = models.FileField("Файл отчета", upload_to='reports/')

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"


# 12. Комментарий (Comment) - Чат
class Comment(models.Model):
    appeal = models.ForeignKey(Appeal, on_delete=models.CASCADE, related_name='comments', verbose_name="Обращение")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Автор")
    text = models.TextField("Текст")
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий (Чат)"
        verbose_name_plural = "Комментарии (Чат)"