from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Application, Category, ApplicationImage
import os


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