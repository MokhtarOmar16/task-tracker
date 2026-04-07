from django.contrib import admin
from .models import Task, TaskCompletion, FriendRequest

# Register your models here.
admin.site.register(Task)
admin.site.register(TaskCompletion)
admin.site.register(FriendRequest)