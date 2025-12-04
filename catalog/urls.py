from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.profile, name='profile'),
    path('create-application/', views.create_application, name='create_application'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('delete-application/<int:pk>/', views.delete_application, name='delete_application'),
    path('admin/applications/', views.admin_application_list, name='admin_application_list'),
    path('admin/applications/<int:pk>/', views.admin_application_detail, name='admin_application_detail'),
]
