from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Task
from .forms import TaskForm


def index(request):
    # Handle form submission for creating a new Task
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.is_completed = False
            task.save()
            messages.success(request, f'Task "{task.title}" created.')
            return redirect('index')
    else:
        form = TaskForm()

    # Uncompleted tasks ordered by due date (soonest due first)
    upcoming_tasks = Task.objects.filter(is_completed=False).order_by('due_date')

    # Completed tasks ordered by due date (soonest due first)
    completed_tasks = Task.objects.filter(is_completed=True).order_by('due_date')

    context = {
        'form': form,
        'upcoming_tasks': upcoming_tasks,
        'completed_tasks': completed_tasks,
    }

    return render(request, 'tasks/index.html', context)


def mark_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not task.is_completed:
        task.is_completed = True
        task.save()
        messages.success(request, f'Task "{task.title}" marked as completed.')
    return redirect('index')


def reopen_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.is_completed:
        task.is_completed = False
        task.save()
        messages.success(request, f'Task "{task.title}" reopened.')
    return redirect('index')


def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    title = task.title
    task.delete()
    messages.success(request, f'Task "{title}" deleted.')
    return redirect('index')
