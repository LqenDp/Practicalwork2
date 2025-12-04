from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.db.models import Count
from django.core.files.storage import FileSystemStorage
from .forms import CustomUserCreationForm, ApplicationForm
from .models import Application, Category, ApplicationImage
from django.contrib.admin.views.decorators import staff_member_required
from .forms import AdminApplicationForm


def index(request):
    completed_applications = Application.objects.filter(
        status='completed'
    ).order_by('-created_at')[:4]

    in_progress_count = Application.objects.filter(status='in_progress').count()

    context = {
        'completed_applications': completed_applications,
        'in_progress_count': in_progress_count,
    }
    return render(request, 'index.html', context)


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'


@login_required
def profile(request):
    return render(request, 'catalog/profile.html')


@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:

                application = form.save(commit=False)
                application.user = request.user
                application.status = 'new'
                application.save()

                image = request.FILES.get('image')
                if image:
                    ApplicationImage.objects.create(
                        application=application,
                        image=image
                    )

                messages.success(request, 'Заявка успешно создана!')
                return redirect('my_applications')
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении заявки: {str(e)}')
    else:
        form = ApplicationForm()

    return render(request, 'catalog/create_application.html', {'form': form})


@login_required
def my_applications(request):
    applications = Application.objects.filter(user=request.user)

    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        'applications': applications,
        'status_filter': status_filter,
    }
    return render(request, 'catalog/my_applications.html', context)


@login_required
def delete_application(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)

    if not application.can_be_deleted():
        messages.error(
            request,
            'Нельзя удалить заявку, которая находится в работе или выполнена'
        )
        return redirect('my_applications')

    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Заявка успешно удалена!')
        return redirect('my_applications')

    return render(request, 'catalog/confirm_delete.html', {'application': application})


@staff_member_required
def admin_application_list(request):
    applications = Application.objects.all()

    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    category_filter = request.GET.get('category')
    if category_filter:
        applications = applications.filter(category_id=category_filter)

    categories = Category.objects.all()

    context = {
        'applications': applications,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
    }
    return render(request, 'catalog/admin_application_list.html', context)


@staff_member_required
def admin_application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if request.method == 'POST':
        form = AdminApplicationForm(request.POST, request.FILES)
        if form.is_valid():

            if not application.can_change_status():
                messages.error(request, 'Нельзя изменить статус заявки, которая уже в работе или выполнена')
                return redirect('admin_application_detail', pk=pk)

            new_status = form.cleaned_data['status']
            application.status = new_status

            if form.cleaned_data.get('comment'):
                application.admin_comment = form.cleaned_data['comment']

            application.save()

            design_image = form.cleaned_data.get('design_image')
            if design_image and new_status == 'completed':
                ApplicationImage.objects.create(
                    application=application,
                    image=design_image,
                    image_type='design'
                )

            messages.success(request, f'Статус заявки успешно изменен на "{application.get_status_display()}"')
            return redirect('admin_application_list')
    else:
        form = AdminApplicationForm(initial={'status': application.status})

    context = {
        'application': application,
        'form': form,
    }
    return render(request, 'catalog/admin_application_detail.html', context)