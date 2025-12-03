from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.db.models import Count
from django.core.files.storage import FileSystemStorage
from .forms import CustomUserCreationForm, ApplicationForm
from .models import Application, Category, ApplicationImage


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