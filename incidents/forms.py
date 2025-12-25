from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Appeal, Comment

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'fio', 'phone', 'department', 'email']

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class AppealForm(forms.ModelForm):
    class Meta:
        model = Appeal
        fields = ['topic', 'category', 'priority', 'description']

    def __init__(self, *args, **kwargs):
        super(AppealForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        self.fields['description'].widget.attrs.update({'rows': 4})

        self.fields['priority'].label_from_instance = lambda obj: f"{obj.level} — {obj.description}"

        self.fields['category'].label_from_instance = lambda obj: f"{obj.name} ({obj.description})"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Напишите сообщение...'
        })
        self.fields['text'].label = ""