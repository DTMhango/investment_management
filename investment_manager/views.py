from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Client, Investment, Contribution
from .forms import SignUpForm

@login_required
def home(request):
    
    context = {
        'title': 'Home',
        'clients': Client.objects.all()
    }
    return render(request, 'investment_manager/home.html', context)

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in. Welcome back!")
            return redirect('home')
        else:
            messages.error(request, "Invalid Username or Password! Please try again.")
            return render(request, 'investment_manager/login.html')
    else:
        return render(request, 'investment_manager/login.html')

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect('login')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()

            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You Have Successfully Registered. Welcome to LISP!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'investment_manager/register.html', {'form': form})
    
    return render(request, 'investment_manager/register.html', {'form': form})

def about(request):
    return render(
        request,
        'investment_manager/about.html',
        {'title': 'About'}
    )
