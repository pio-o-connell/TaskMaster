from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('task/<int:pk>/complete/', views.mark_complete, name='task-complete'),
    path('task/<int:pk>/reopen/', views.reopen_task, name='task-reopen'),
    path('task/<int:pk>/delete/', views.delete_task, name='task-delete'),
]
