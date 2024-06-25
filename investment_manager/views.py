from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Client, Investment, Contribution
from .forms import SignUpForm, CreateClientForm, CreateContributionForm, CreateInvestmentForm
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Sum

@login_required
def home(request):
    
    return render(request, 'investment_manager/home.html', {})

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


def all_client_data(request):
    if request.user.is_authenticated:
        # look up client data
        context = {
        'clients': Client.objects.all()
    }
        return render(request, 'investment_manager/clients.html', context)
    else:
        messages.success(request, 'You Must Be Logged in to View Client Records!')
        return redirect('login')
    

def all_contribution_data(request):
    if request.user.is_authenticated:
        # client = get_object_or_404(Client)
        contributions = Contribution.objects.all()
        context = {
            'contributions': contributions 
        }
        return render(request, 'investment_manager/all_client_contributions.html', context)


def all_investment_data(request):
    if request.user.is_authenticated:
        # Example of fetching investments for a specific client
        # client = get_object_or_404(Client, pk=request.GET.get('client_id'))
        investments = Investment.objects.all()
        context = {
            'investments': investments
        }
        return render(request, 'investment_manager/all_client_investments.html', context)
    
@login_required
def individual_client_data(request, pk):
    client_data = get_object_or_404(Client, pk=pk)
    return render(request, 'investment_manager/individual_client.html', {'client_data': client_data})


@login_required
def individual_contribution_data(request, pk):
    client = Client.objects.get(id=pk)
    contributions = Contribution.objects.filter(client=client)
    total_contributions = contributions.count()
    total_amount_contributed = contributions.aggregate(Sum('contribution_amount'))['contribution_amount__sum'] or 0
    total_fees = contributions.aggregate(Sum('fees'))['fees__sum'] or 0

    context = {
        'client_data': client,
        'contributions': contributions,
        'total_contributions': total_contributions,
        'total_amount_contributed': total_amount_contributed,
        'total_fees': total_fees,
    }
    return render(request, 'investment_manager/individual_contributions.html', context)


@login_required
def individual_investment_data(request, pk):
    client = get_object_or_404(Client, id=pk)
    investments = Investment.objects.filter(client=client)
    total_investments = investments.count()
    total_amount_invested = investments.aggregate(Sum('investment_amount'))['investment_amount__sum'] or 0

    context = {
        'client_data': client,
        'investments': investments,
        'total_investments': total_investments,
        'total_amount_invested': total_amount_invested,
    }
    return render(request, 'investment_manager/individual_investments.html', context)



@login_required
def create_client(request):
    if request.method == 'POST':
        form = CreateClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.manager = request.user
            client.save()
            messages.success(request, "Client Added Successfully!")
            return HttpResponseRedirect(reverse('create_client'))  # Redirect to the same view
    else:
        form = CreateClientForm()
    return render(request, 'investment_manager/create_client.html', {'form': form})


@login_required
def create_contribution(request, client_id):
    if request.method == 'POST':
        form = CreateContributionForm(request.POST, client_id=client_id)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.manager = request.user
            contribution.save()
            messages.success(request, "Contribution Added Successfully!")
            return HttpResponseRedirect(reverse('create_contribution', args=[client_id]))  # Redirect to the same view
    else:
        form = CreateContributionForm(client_id=client_id)
    return render(request, 'investment_manager/create_contribution.html', {'form': form})


@login_required
def create_investment(request, client_id):
    if request.method == 'POST':
        form = CreateInvestmentForm(request.POST, client_id=client_id)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.manager = request.user
            investment.save()
            messages.success(request, "Investment Added Successfully!")
            return HttpResponseRedirect(reverse('create_investment', args=[client_id]))  # Redirect to the same view
    else:
        form = CreateInvestmentForm(client_id=client_id)
    return render(request, 'investment_manager/create_investment.html', {'form': form})


def about(request):
    return render(
        request,
        'investment_manager/about.html',
        {'title': 'About'}
    )

@login_required
def update_records(request):
    if request.method == 'POST':
        investments = Investment.objects.all()
        for investment in investments:
            try:
                investment.save(validate=False)  # Bypass validation
            except ValidationError as e:
                messages.error(request, f"Failed to update investment {investment.id}: {e}")
        messages.success(request, "All valid Investment Records updated")
    return render(request, 'investment_manager/update_records.html', {})
