
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Category, Application, ApplicationImage
from .forms import AdminApplicationForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'applications_count')
    search_fields = ('name',)

    def applications_count(self, obj):
        return obj.application_set.count()

    applications_count.short_description = 'Количество заявок'


class ApplicationImageInline(admin.TabularInline):
    model = ApplicationImage
    extra = 0
    readonly_fields = ('uploaded_at', 'image_type', 'preview')
    fields = ('image_type', 'image', 'preview', 'uploaded_at')

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
        return "Нет изображения"

    preview.short_description = 'Предпросмотр'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    form = AdminApplicationForm
    list_display = ('title', 'user', 'category', 'status', 'created_at', 'admin_actions')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'user__username', 'description')
    readonly_fields = ('created_at', 'user', 'title', 'description', 'category', 'can_change_status_display')
    fieldsets = (
        ('Информация о заявке', {
            'fields': ('user', 'title', 'description', 'category', 'created_at')
        }),
        ('Управление статусом', {
            'fields': ('status', 'comment', 'design_image', 'can_change_status_display')
        }),
    )
    inlines = [ApplicationImageInline]

    def can_change_status_display(self, obj):
        if obj.can_change_status():
            return " Можно изменить статус"
        return " Нельзя изменить статус (уже в работе или выполнено)"

    can_change_status_display.short_description = 'Возможность изменения статуса'

    def admin_actions(self, obj):
        if obj.can_change_status():
            return format_html('<span style="color: green;">Доступно изменение статуса</span>')
        return format_html('<span style="color: gray;">Статус фиксирован</span>')

    admin_actions.short_description = 'Действия'

    def save_model(self, request, obj, form, change):

        if form.cleaned_data.get('comment'):
            obj.admin_comment = form.cleaned_data['comment']

        design_image = form.cleaned_data.get('design_image')
        if design_image and obj.status == 'completed':
            ApplicationImage.objects.create(
                application=obj,
                image=design_image,
                image_type='design'
            )

        super().save_model(request, obj, form, change)


@admin.register(ApplicationImage)
class ApplicationImageAdmin(admin.ModelAdmin):
    list_display = ('application', 'image_type', 'uploaded_at', 'preview')
    list_filter = ('image_type', 'uploaded_at')
    readonly_fields = ('uploaded_at', 'preview')

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
        return "Нет изображения"

    preview.short_description = 'Предпросмотр'