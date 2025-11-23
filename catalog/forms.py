from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=100,
        label='ФИО',
        help_text='Введите ваше полное имя'
    )
    email = forms.EmailField(required=True)
    agreement = forms.BooleanField(
        required=True,
        label='Согласие на обработку персональных данных'
    )

    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'password1', 'password2', 'agreement')