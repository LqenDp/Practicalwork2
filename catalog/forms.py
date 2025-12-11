from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import Application, Category, ApplicationImage
import os


class CustomUserCreationForm(forms.Form):  # Изменяем на forms.Form вместо UserCreationForm
    username = forms.CharField(
        max_length=150,
        label='Имя пользователя',
        help_text='Требуется. Не более 150 символов. Только буквы, цифры и @/./+/-/_',
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя пользователя'})
    )

    full_name = forms.CharField(
        max_length=100,
        label='ФИО',
        help_text='Введите ваше полное имя',
        widget=forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'})
    )

    email = forms.CharField(
        max_length=254,
        label='Электронная почта',
        help_text='Введите адрес электронной почты (должен содержать @)',
        widget=forms.TextInput(attrs={'placeholder': 'example@domain'}),
        required=True
    )

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}),
        required=True
    )

    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}),
        required=True
    )

    agreement = forms.BooleanField(
        required=True,
        label='Согласие на обработку персональных данных'
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()

        if not username:
            raise ValidationError('Имя пользователя обязательно для заполнения')

        # Проверяем уникальность username
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует')

        # Простая проверка на допустимые символы
        import re
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError('Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_')

        return username

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()

        if not full_name:
            raise ValidationError('ФИО обязательно для заполнения')

        return full_name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        if not email:
            raise ValidationError('Email обязателен для заполнения')

        # Простая проверка на наличие @
        if '@' not in email:
            raise ValidationError('Введите корректный адрес электронной почты (должен содержать @)')

        # Проверяем уникальность email
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')

        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if not password1:
            raise ValidationError('Пароль обязателен для заполнения')

        # Минимум 1 символ
        if len(password1) < 1:
            raise ValidationError('Пароль должен содержать хотя бы 1 символ')

        return password1

    def clean_password2(self):
        password2 = self.cleaned_data.get('password2')
        password1 = self.cleaned_data.get('password1')

        if not password2:
            raise ValidationError('Подтверждение пароля обязательно')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")

        return password2

    def clean_agreement(self):
        agreement = self.cleaned_data.get('agreement')

        if not agreement:
            raise ValidationError('Вы должны согласиться на обработку персональных данных')

        return agreement

    def save(self, commit=True):
        # Создаем пользователя вручную
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['full_name']
        )

        return user


# Остальные формы остаются без изменений
class ApplicationForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    image = forms.ImageField(
        label='Фотография помещения',
        help_text='Формат: jpg, jpeg, png, bmp. Максимальный размер: 2МБ',
        required=True
    )

    class Meta:
        model = Application
        fields = ['title', 'description', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in allowed_extensions:
                raise ValidationError(
                    f'Недопустимый формат файла. Разрешенные форматы: {", ".join(allowed_extensions)}'
                )
            if image.size > 2097152:
                raise ValidationError('Размер файла не должен превышать 2 МБ')
        return image


class AdminApplicationForm(forms.ModelForm):
    comment = forms.CharField(
        label='Комментарий администратора',
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,
        help_text='Обязателен при смене статуса на "Принято в работу"'
    )
    design_image = forms.ImageField(
        label='Изображение дизайна',
        required=False,
        help_text='Обязательно при смене статуса на "Выполнено". Формат: jpg, jpeg, png, bmp. Максимальный размер: 2МБ'
    )

    class Meta:
        model = Application
        fields = ['status', 'comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        comment = cleaned_data.get('comment')
        design_image = self.files.get('design_image') if hasattr(self, 'files') else None

        if status == 'in_progress' and not comment:
            raise ValidationError('При смене статуса на "Принято в работу" необходим комментарий')

        if status == 'completed' and not design_image:
            raise ValidationError('При смене статуса на "Выполнено" необходимо прикрепить изображение дизайна')

        return cleaned_data

    def clean_design_image(self):
        design_image = self.cleaned_data.get('design_image')
        if design_image:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            ext = os.path.splitext(design_image.name)[1].lower()
            if ext not in allowed_extensions:
                raise ValidationError(
                    f'Недопустимый формат файла. Разрешенные форматы: {", ".join(allowed_extensions)}'
                )
            if design_image.size > 2097152:
                raise ValidationError('Размер файла не должен превышать 2 МБ')
        return design_image