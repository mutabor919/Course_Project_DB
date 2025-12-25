from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login

from django.contrib.auth.decorators import login_required

from .models import Role, Appeal, Status, Comment, ActionLog, Assignment, Department, Report
from .forms import UserRegistrationForm, AppealForm, CommentForm

import csv
import json
from django.http import HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

import os
from django.conf import settings

# Импорты для PDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from django.core.management import call_command
from django.contrib import messages

from django.utils import timezone

from django.core.files.base import ContentFile

import io

def index(request):
    return render(request, 'incidents/index.html')

def log_action(user, appeal, action, description=""):
    ActionLog.objects.create(
        user=user,
        appeal=appeal,
        action_type=action,
        description=description
    )

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            try:
                user.role = Role.objects.get(name="User")
            except Role.DoesNotExist:
                pass
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'incidents/register.html', {'form': form})


@login_required
def my_appeals(request):
    if request.user.role.name in ['Admin', 'Staff']:
        appeals = Appeal.objects.all().order_by('-created_at')
    else:
        appeals = Appeal.objects.filter(applicant=request.user).order_by('-created_at')

    return render(request, 'incidents/appeals_list.html', {'appeals': appeals})

@login_required
def create_appeal(request):
    if request.method == 'POST':
        form = AppealForm(request.POST)
        if form.is_valid():
            appeal = form.save(commit=False)
            appeal.applicant = request.user
            try:
                appeal.status = Status.objects.get(name="Новое")
            except Status.DoesNotExist:
                pass
            appeal.save()
            return redirect('my_appeals')
    else:
        form = AppealForm()
    return render(request, 'incidents/create_appeal.html', {'form': form})


@login_required
def appeal_detail(request, pk):
    appeal = get_object_or_404(Appeal, pk=pk)

    if request.user.role.name == 'User' and appeal.applicant != request.user:
        return render(request, 'incidents/403.html', status=403)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.appeal = appeal
            comment.author = request.user
            comment.save()
            return redirect('appeal_detail', pk=pk)
    else:
        form = CommentForm()

    logs = ActionLog.objects.filter(appeal=appeal).order_by('-timestamp')

    return render(request, 'incidents/appeal_detail.html', {
        'appeal': appeal,
        'form': form,
        'logs': logs
    })


# Экспорт данных
@login_required
def export_appeals_csv(request):
    if request.user.role.name not in ['Admin', 'Staff']:
        return render(request, 'incidents/403.html', status=403)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="appeals_report.csv"'
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';')

    writer.writerow(['ID', 'Тема', 'Заявитель', 'Статус', 'Категория', 'Приоритет', 'Дата создания'])

    appeals = Appeal.objects.all().order_by('-created_at')
    for appeal in appeals:
        writer.writerow([
            appeal.id,
            appeal.topic,
            appeal.applicant.fio,
            appeal.status.name,
            appeal.category.name,
            appeal.priority.level,
            appeal.created_at.strftime("%d.%m.%Y %H:%M"),
        ])

    return response


@login_required
def export_appeals_json(request):
    if request.user.role.name not in ['Admin', 'Staff']:
        return render(request, 'incidents/403.html', status=403)

    appeals = Appeal.objects.all().values(
        'id', 'topic', 'status__name', 'category__name', 'priority__level', 'created_at'
    )
    data = list(appeals)
    return JsonResponse(data, safe=False, encoder=DjangoJSONEncoder, json_dumps_params={'ensure_ascii': False})


@login_required
def export_appeals_pdf(request):
    if request.user.role.name not in ['Admin', 'Staff']:
        return render(request, 'incidents/403.html', status=403)

    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DejaVuSans.ttf')
    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    styles['Title'].fontName = 'DejaVuSans'
    elements.append(Paragraph("Отчет по инцидентам ИБ", styles['Title']))
    elements.append(Paragraph(f"Сформирован: {timezone.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    data = [['ID', 'Тема', 'Статус', 'Категория', 'Дата']]
    appeals = Appeal.objects.all().order_by('-created_at')

    style_body = styles['Normal']
    style_body.fontName = 'DejaVuSans'
    style_body.fontSize = 9

    for appeal in appeals:
        topic = Paragraph(appeal.topic, style_body)
        row = [str(appeal.id), topic, appeal.status.name, appeal.category.name, appeal.created_at.strftime("%d.%m.%Y")]
        data.append(row)

    table = Table(data, colWidths=[30, 200, 80, 100, 80])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(table)

    doc.build(elements)

    pdf_value = buffer.getvalue()
    filename = f"report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    report = Report.objects.create(
        initiator=request.user,
        report_type="PDF",
        appeal_count=appeals.count()
    )

    report.file_path.save(filename, ContentFile(pdf_value))
    report.save()

    log_action(request.user, None, "Генерация отчета", f"Создан отчет ID #{report.id} ({filename})")

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def trigger_backup(request):
    if request.user.role.name != 'Admin':
        return render(request, 'incidents/403.html', status=403)

    try:
        call_command('create_backup')

        messages.success(request, '✅ Бэкап успешно создан и отправлен в облако!')

    except Exception as e:
        messages.error(request, f'❌ Ошибка при создании бэкапа: {e}')

    return redirect('my_appeals')


@login_required
def take_appeal(request, pk):
    if request.user.role.name not in ['Staff', 'Admin']:
        return render(request, 'incidents/403.html', status=403)

    appeal = get_object_or_404(Appeal, pk=pk)

    try:
        status_in_progress = Status.objects.get(name="В работе")
        appeal.status = status_in_progress
        appeal.save()

        Assignment.objects.create(
            appeal=appeal,
            performer=request.user,
            comment="Сотрудник взял заявку в работу через интерфейс"
        )

        log_action(request.user, appeal, "Смена статуса", "Заявка переведена в статус 'В работе'")
        log_action(request.user, appeal, "Назначение", f"Исполнителем назначен: {request.user.fio}")

        messages.success(request, f"Вы взяли заявку #{appeal.id} в работу!")

    except Status.DoesNotExist:
        messages.error(request, "Ошибка: Статус 'В работе' не найден в справочнике.")

    return redirect('appeal_detail', pk=pk)

@login_required
def close_appeal(request, pk):
    if request.user.role.name not in ['Staff', 'Admin']:
        return render(request, 'incidents/403.html', status=403)

    appeal = get_object_or_404(Appeal, pk=pk)

    try:
        status_closed = Status.objects.get(name="Закрыто")
        appeal.status = status_closed
        appeal.closed_at = timezone.now()
        appeal.save()

        log_action(request.user, appeal, "Закрытие заявки", "Инцидент устранен, заявка закрыта.")

        messages.success(request, f"Заявка #{appeal.id} успешно закрыта.")

    except Status.DoesNotExist:
        messages.error(request, "Ошибка: Статус 'Закрыто' не найден.")

    return redirect('appeal_detail', pk=pk)


@login_required
def report_history(request):
    if request.user.role.name not in ['Admin', 'Staff']:
        return render(request, 'incidents/403.html', status=403)

    reports = Report.objects.all().order_by('-created_at')
    return render(request, 'incidents/reports_list.html', {'reports': reports})