from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser, CheckingAccount, SavingsAccount
from .forms import CustomUserCreationForm, CustomAuthenticationForm

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, email=email, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'signin.html', {'form': form})

@login_required
def welcome(request):
    # Get the name of the logged-in user
    name = request.user.username

    from .models import CustomUser
    user = CustomUser.objects.get(email=request.user.email)

    # Render the welcome template with the user's name
    return render(request, 'welcome.html', {'name': name, 'user': user})

@login_required
def checking(request):
    # Get the checking account for the logged-in user
    user = CustomUser.objects.get(email=request.user.email)
    checking_account = CheckingAccount.objects.get(user=user)

    # Render the checking template with the user's checking account balance
    return render(request, 'checking.html', {'balance': checking_account.balance})

@login_required
def savings(request):
    # Get the savings account for the logged-in user
    user = CustomUser.objects.get(email=request.user.email)
    savings_account = SavingsAccount.objects.get(user=user)

    # Render the savings template with the user's savings account balance
    return render(request, 'savings.html', {'balance': savings_account.balance})
