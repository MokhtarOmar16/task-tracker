from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from .forms import CustomUserCreationForm


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
