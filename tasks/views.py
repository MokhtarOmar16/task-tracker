from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Task, TaskCompletion


@login_required
def dashboard(request):
    today = timezone.now().date()
    tasks = Task.objects.filter(user=request.user, created_at__date=today).order_by(
        "-created_at"
    )
    completed_count = tasks.filter(completed_at__isnull=False).count()
    total_count = tasks.count()
    progress_percent = 0
    if total_count > 0:
        progress_percent = int((completed_count / total_count) * 100)
    return render(
        request,
        "tasks/dashboard.html",
        {
            "tasks": tasks,
            "completed_count": completed_count,
            "total_count": total_count,
            "progress_percent": progress_percent,
        },
    )


@login_required
def create_task(request):
    if request.method == "POST":
        title = request.POST.get("title")
        notes = request.POST.get("notes")
        is_public = request.POST.get("is_public") == "on"

        Task.objects.create(
            user=request.user, title=title, notes=notes, is_public=is_public
        )
        return redirect("dashboard")
    return render(request, "tasks/create_task.html")


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect("dashboard")


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if not task.completed_at:
        task.completed_at = timezone.now()
        task.save()
        TaskCompletion.objects.create(task=task)
    return redirect("dashboard")


@login_required
def history(request):
    tasks = Task.objects.filter(user=request.user, completed_at__isnull=False).order_by(
        "-completed_at"
    )
    return render(request, "tasks/history.html", {"tasks": tasks})
