from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("create/", views.create_task, name="create_task"),
    path("delete/<int:task_id>/", views.delete_task, name="delete_task"),
    path("complete/<int:task_id>/", views.complete_task, name="complete_task"),
    path("history/", views.history, name="history"),
]
