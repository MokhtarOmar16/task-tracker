from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("create/", views.create_task, name="create_task"),
    path("delete/<int:task_id>/", views.delete_task, name="delete_task"),
    path("complete/<int:task_id>/", views.complete_task, name="complete_task"),
    path("edit/<int:task_id>/", views.edit_task, name="edit_task"),
    path("history/", views.history, name="history"),
    path("calendar/", views.calendar, name="calendar"),
    path("friends/", views.friends, name="friends"),
    path(
        "friends/request/<int:user_id>/",
        views.send_friend_request,
        name="send_friend_request",
    ),
    path(
        "friends/accept/<int:request_id>/",
        views.accept_friend_request,
        name="accept_friend_request",
    ),
    path(
        "friends/decline/<int:request_id>/",
        views.decline_friend_request,
        name="decline_friend_request",
    ),
    path("friends/remove/<int:user_id>/", views.remove_friend, name="remove_friend"),
    path("feed/", views.social_feed, name="social_feed"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
]
