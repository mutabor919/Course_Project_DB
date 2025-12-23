from django.shortcuts import render, redirect
from django.contrib.auth import login
# Вот этой строки не хватало:
from django.contrib.auth.decorators import login_required

from .models import Role, Appeal, Status
from .forms import UserRegistrationForm, AppealForm

def index(request):
    return render(request, 'incidents/index.html')

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