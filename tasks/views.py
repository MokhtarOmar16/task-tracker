from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange
from django.db.models import Count
from django.db.models import Q
from .models import Task, TaskCompletion, FriendRequest

User = get_user_model()


@login_required
def dashboard(request):
    today = timezone.now().date()
    tasks = Task.objects.filter(
        user=request.user, created_at__date=today, completed_at__isnull=True
    ).order_by("-created_at")
    completed_today = Task.objects.filter(
        user=request.user, created_at__date=today, completed_at__isnull=False
    ).order_by("-completed_at")
    completed_count = completed_today.count()
    total_count = tasks.count()
    progress_percent = 0
    if total_count + completed_count > 0:
        progress_percent = int(
            (completed_count / (total_count + completed_count)) * 100
        )

    all_users = User.objects.all()

    leaderboard_data = []
    for user in all_users:
        completed_tasks = Task.objects.filter(
            user=user, completed_at__date=today
        ).count()
        leaderboard_data.append(
            {
                "user": user,
                "completed_tasks": completed_tasks,
                "current_streak": user.current_streak,
                "longest_streak": user.longest_streak,
            }
        )

    leaderboard_data.sort(key=lambda x: x["completed_tasks"], reverse=True)

    for i, entry in enumerate(leaderboard_data):
        entry["rank"] = i + 1

    total_daily = total_count + completed_count

    return render(
        request,
        "tasks/dashboard.html",
        {
            "tasks": tasks,
            "completed_today": completed_today,
            "completed_count": completed_count,
            "total_count": total_count,
            "total_daily": total_daily,
            "progress_percent": progress_percent,
            "leaderboard": leaderboard_data,
        },
    )


@login_required
def get_leaderboard_data(request):
    from django.db.models import Count

    friends_list = []
    for fr in FriendRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user), status="accepted"
    ):
        if fr.from_user == request.user:
            friends_list.append(fr.to_user)
        else:
            friends_list.append(fr.from_user)

    friends_list.append(request.user)

    leaderboard_data = []
    for user in friends_list:
        completed_tasks = Task.objects.filter(
            user=user, completed_at__isnull=False
        ).count()
        leaderboard_data.append(
            {
                "user": user,
                "completed_tasks": completed_tasks,
                "current_streak": user.current_streak,
                "longest_streak": user.longest_streak,
            }
        )

    leaderboard_data.sort(key=lambda x: (-x["completed_tasks"], -x["current_streak"]))

    for i, entry in enumerate(leaderboard_data):
        entry["rank"] = i + 1

    return leaderboard_data


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
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "POST":
        task.title = request.POST.get("title")
        task.notes = request.POST.get("notes")
        task.is_public = request.POST.get("is_public") == "on"
        task.save()
        return redirect("dashboard")

    return render(request, "tasks/edit_task.html", {"task": task})


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if not task.completed_at:
        task.completed_at = timezone.now()
        task.save()
        TaskCompletion.objects.create(task=task)
    return redirect("dashboard")


@login_required
def uncomplete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if task.completed_at:
        task.completed_at = None
        task.save()
        TaskCompletion.objects.filter(task=task).delete()
    return redirect("dashboard")


@login_required
def history(request):
    tasks = Task.objects.filter(user=request.user, completed_at__isnull=False).order_by(
        "-completed_at"
    )
    return render(request, "tasks/history.html", {"tasks": tasks})


@login_required
def calendar(request):
    today = timezone.now().date()
    year = request.GET.get("y")
    month = request.GET.get("m")

    if year and month:
        try:
            year = int(year)
            month = int(month)
        except (ValueError, TypeError):
            year = today.year
            month = today.month
    else:
        year = today.year
        month = today.month

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    _, last_day = monthrange(year, month)

    first_day = datetime(year, month, 1)
    last_day_date = datetime(year, month, last_day)

    start_date = first_day.date()
    end_date = last_day_date.date() + timedelta(days=1)

    completed_tasks = Task.objects.filter(
        user=request.user, completed_at__gte=start_date, completed_at__lt=end_date
    ).order_by("-completed_at")

    task_counts_by_date = {}
    for task in completed_tasks:
        date_key = task.completed_at.date()
        if date_key not in task_counts_by_date:
            task_counts_by_date[date_key] = []
        task_counts_by_date[date_key].append(task)

    task_counts_list = [
        (date, len(tasks)) for date, tasks in task_counts_by_date.items()
    ]

    calendar_weeks = []
    first_weekday = first_day.weekday()

    week = [None] * first_weekday

    for day in range(1, last_day + 1):
        week.append(datetime(year, month, day).date())
        if len(week) == 7:
            calendar_weeks.append(week)
            week = []

    if week:
        while len(week) < 7:
            week.append(None)
        calendar_weeks.append(week)

    streak_days = calculate_streak(request.user)

    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    month_name = first_day.strftime("%B")

    return render(
        request,
        "tasks/calendar.html",
        {
            "year": year,
            "month": month,
            "month_name": month_name,
            "calendar_weeks": calendar_weeks,
            "task_counts_by_date": task_counts_by_date,
            "task_counts_list": task_counts_list,
            "streak_days": streak_days,
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month,
            "today": today,
        },
    )


def calculate_streak(user):
    today = timezone.now().date()
    streak_days = []
    current_date = today

    while True:
        has_completed = Task.objects.filter(
            user=user, completed_at__date=current_date
        ).exists()

        if has_completed:
            streak_days.append(current_date)
            current_date -= timedelta(days=1)
        else:
            break

        if len(streak_days) > 365:
            break

    user.current_streak = len(streak_days)

    if user.longest_streak < user.current_streak:
        user.longest_streak = user.current_streak

    user.save()

    return streak_days


@login_required
def friends(request):
    sent_requests = FriendRequest.objects.filter(
        from_user=request.user, status="pending"
    )
    received_requests = FriendRequest.objects.filter(
        to_user=request.user, status="pending"
    )

    friends_list = []
    for fr in FriendRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user), status="accepted"
    ):
        if fr.from_user == request.user:
            friends_list.append(fr.to_user)
        else:
            friends_list.append(fr.from_user)

    search_query = request.GET.get("q", "")
    search_results = []
    if search_query:
        search_results = User.objects.filter(username__icontains=search_query).exclude(
            id=request.user.id
        )
        for fr in friends_list:
            search_results = search_results.exclude(id=fr.id)
        for sr in sent_requests:
            search_results = search_results.exclude(id=sr.to_user.id)
        for rr in received_requests:
            search_results = search_results.exclude(id=rr.from_user.id)
        search_results = list(search_results)[:10]

    suggested_users = User.objects.exclude(id=request.user.id)
    for fr in friends_list:
        suggested_users = suggested_users.exclude(id=fr.id)
    for sr in sent_requests:
        suggested_users = suggested_users.exclude(id=sr.to_user.id)
    for rr in received_requests:
        suggested_users = suggested_users.exclude(id=rr.from_user.id)
    suggested_users = list(
        suggested_users.order_by("-longest_streak", "-current_streak")[:5]
    )

    return render(
        request,
        "tasks/friends.html",
        {
            "friends_list": friends_list,
            "sent_requests": sent_requests,
            "received_requests": received_requests,
            "search_results": search_results,
            "search_query": search_query,
            "suggested_users": suggested_users,
        },
    )


@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)

    if to_user == request.user:
        messages.error(request, "You cannot send a friend request to yourself.")
        return redirect("friends")

    existing_request = FriendRequest.objects.filter(
        (
            Q(from_user=request.user, to_user=to_user)
            | Q(from_user=to_user, to_user=request.user)
        ),
        status="pending",
    ).first()

    if existing_request:
        messages.info(request, "A friend request already exists.")
        return redirect("friends")

    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    messages.success(request, f"Friend request sent to {to_user.username}")
    return redirect("friends")


@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(
        FriendRequest, id=request_id, to_user=request.user, status="pending"
    )
    friend_request.status = "accepted"
    friend_request.save()
    messages.success(
        request, f"You are now friends with {friend_request.from_user.username}"
    )
    return redirect("friends")


@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(
        FriendRequest, id=request_id, to_user=request.user, status="pending"
    )
    friend_request.status = "declined"
    friend_request.save()
    messages.info(request, "Friend request declined")
    return redirect("friends")


@login_required
def remove_friend(request, user_id):
    friend_user = get_object_or_404(User, id=user_id)
    friendship = FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=friend_user)
        | Q(from_user=friend_user, to_user=request.user),
        status="accepted",
    ).first()

    if friendship:
        friendship.status = "removed"
        friendship.save()
        messages.success(request, f"Removed {friend_user.username} from friends")
    else:
        messages.error(request, "Friendship not found")

    return redirect("friends")


@login_required
def social_feed(request):
    friends_list = []
    for fr in FriendRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user), status="accepted"
    ):
        if fr.from_user == request.user:
            friends_list.append(fr.to_user)
        else:
            friends_list.append(fr.from_user)

    all_friend_tasks = Task.objects.filter(
        user__in=friends_list, is_public=True
    ).order_by("-created_at")[:30]

    return render(
        request,
        "tasks/social_feed.html",
        {
            "friend_tasks": all_friend_tasks,
            "friends_list": friends_list,
        },
    )


@login_required
def leaderboard(request):
    today = timezone.now().date()
    friends_list = []
    for fr in FriendRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user), status="accepted"
    ):
        if fr.from_user == request.user:
            friends_list.append(fr.to_user)
        else:
            friends_list.append(fr.from_user)

    friends_list.append(request.user)

    leaderboard_data = []
    for user in friends_list:
        completed_today = Task.objects.filter(
            user=user, completed_at__date=today
        ).count()
        leaderboard_data.append(
            {
                "user": user,
                "completed_tasks": completed_today,
                "current_streak": user.current_streak,
                "longest_streak": user.longest_streak,
            }
        )

    leaderboard_data.sort(key=lambda x: x["completed_tasks"], reverse=True)

    leaderboard_by_streak = sorted(leaderboard_data, key=lambda x: -x["current_streak"])
    leaderboard_by_best = sorted(leaderboard_data, key=lambda x: -x["longest_streak"])

    for i, entry in enumerate(leaderboard_data):
        entry["rank"] = i + 1

    return render(
        request,
        "tasks/leaderboard.html",
        {
            "leaderboard": leaderboard_data,
            "leaderboard_by_streak": leaderboard_by_streak,
            "leaderboard_by_best": leaderboard_by_best,
            "friends_list": friends_list,
        },
    )


def global_leaderboard(request):
    today = timezone.now().date()
    all_users = User.objects.all()

    leaderboard_data = []
    for user in all_users:
        completed_today = Task.objects.filter(
            user=user, completed_at__date=today
        ).count()
        leaderboard_data.append(
            {
                "user": user,
                "completed_tasks": completed_today,
                "current_streak": user.current_streak,
                "longest_streak": user.longest_streak,
            }
        )

    leaderboard_data.sort(key=lambda x: x["completed_tasks"], reverse=True)

    leaderboard_by_streak = sorted(leaderboard_data, key=lambda x: -x["current_streak"])
    leaderboard_by_best = sorted(leaderboard_data, key=lambda x: -x["longest_streak"])

    for i, entry in enumerate(leaderboard_data):
        entry["rank"] = i + 1

    return render(
        request,
        "tasks/global_leaderboard.html",
        {
            "leaderboard": leaderboard_data,
            "leaderboard_by_streak": leaderboard_by_streak,
            "leaderboard_by_best": leaderboard_by_best,
        },
    )
