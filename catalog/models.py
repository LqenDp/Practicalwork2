from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os


class Category(models.Model):
    name = models.CharField(max_length=200, help_text="Введите категорию дизайна")

    def __str__(self):
        return self.name


class Application(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('completed', 'Выполнено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Временная метка')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def can_be_deleted(self):
        return self.status in ['new']

class ApplicationImage(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='applications/',
        verbose_name='Фотография',
        validators=[]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Фото для {self.application.title}"