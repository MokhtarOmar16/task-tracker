from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

User = get_user_model()


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f"Welcome to TaskFlow! Your account has been created."
            )
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    from django.contrib.auth.views import LoginView

    return LoginView.as_view(template_name="registration/login.html")(request)


@require_GET
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def profile(request, username=None):
    from tasks.models import Task, FriendRequest
    from django.db.models import Q

    if username:
        view_user = get_object_or_404(User, username=username)
    else:
        view_user = request.user

    total_all = Task.objects.filter(user=view_user, completed_at__isnull=False).count()

    if view_user == request.user:
        total_tasks = total_all
        recent_tasks = Task.objects.filter(
            user=view_user, completed_at__isnull=False
        ).order_by("-completed_at")[:5]
    else:
        total_tasks = Task.objects.filter(
            user=view_user,
            completed_at__isnull=False,
        ).count()
        recent_tasks = Task.objects.filter(
            user=view_user, completed_at__isnull=False, is_public=True
        ).order_by("-completed_at")[:5]

    friends_count = FriendRequest.objects.filter(
        Q(from_user=view_user) | Q(to_user=view_user), status="accepted"
    ).count()

    is_own = view_user == request.user

    is_friend = False
    request_sent = False
    request_received = False

    if not is_own:
        is_friend = FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=view_user)
            | Q(from_user=view_user, to_user=request.user),
            status="accepted",
        ).exists()

        request_sent = FriendRequest.objects.filter(
            from_user=request.user, to_user=view_user, status="pending"
        ).exists()

        request_received = FriendRequest.objects.filter(
            from_user=view_user, to_user=request.user, status="pending"
        ).exists()

    return render(
        request,
        "accounts/profile.html",
        {
            "total_tasks": total_tasks,
            "friends_count": friends_count,
            "recent_tasks": recent_tasks,
            "view_user": view_user,
            "is_own": is_own,
            "is_friend": is_friend,
            "request_sent": request_sent,
            "request_received": request_received,
        },
    )


@login_required
@require_POST
def edit_profile(request):
    user = request.user
    user.full_name = request.POST.get("full_name", "")
    user.bio = request.POST.get("bio", "")

    goal = request.POST.get("task_goal")
    if goal:
        try:
            user.task_goal = int(goal)
        except ValueError:
            pass

    user.save()
    messages.success(request, "Profile updated successfully!")
    return redirect("profile")


def edit_profile_page(request):
    return render(request, "accounts/edit_profile.html")
