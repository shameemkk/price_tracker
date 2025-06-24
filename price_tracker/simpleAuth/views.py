from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction


# Create your views here.
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')
    

def register(request):
    if request.method == "POST":
        email = request.POST.get("email").strip().lower()
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if not email or not password or not confirm_password:
            messages.error(request, 'All fields are required.')
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        try:
            with transaction.atomic():
                user = User.objects.create_user(username=email, email=email, password=password)
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error during registration: {str(e)}')
            return redirect('register')
    return render(request, "auth/register.html")

def login(request):
    if request.method == "POST":
        email = request.POST.get("email").strip().lower()
        password = request.POST.get("password")
        if not email or not password:
            messages.error(request, 'Both fields are required.')
            return redirect('login')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')
    return render(request, "auth/login.html")