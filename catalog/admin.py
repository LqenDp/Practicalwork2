# catalog/admin.py
from django.contrib import admin
from .models import Category, Application, ApplicationImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'user__username', 'description')
    readonly_fields = ('created_at',)

