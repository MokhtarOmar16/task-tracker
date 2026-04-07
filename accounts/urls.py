from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile_page, name="edit_profile"),
    path("profile/save/", views.edit_profile, name="save_profile"),
    path("profile/<str:username>/", views.profile, name="user_profile"),
]
