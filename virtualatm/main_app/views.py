from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models_customs import CustomUser
from .models import CheckingAccount, SavingsAccount,  CheckingTransaction, Transaction
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .forms import CheckingDepositForm, CheckingWithdrawalForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View, Q


# Create your views here.

def home(request):
    return render(request, 'home.html')
    
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, email=email, password=password)
            login(request, user)
            return redirect('welcome')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            login(request, user)
            return redirect('welcome')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'signin.html', {'form': form})

@login_required
def welcome(request):
    # Get the name of the logged-in user
    first_name = request.user.first_name
    from .models import CustomUser
    user = CustomUser.objects.get(email=request.user.email)

    # Render the welcome template with the user's name
    return render(request, 'welcome.html', {'first_name': first_name})

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

class CheckingBalanceView(LoginRequiredMixin, TemplateView):
    template_name = 'main_app/checking_balance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        try:
            checking_account = CheckingAccount.objects.get(user=user)
            context['balance'] = checking_account.balance
        except CheckingAccount.DoesNotExist:
            context['balance'] = 0
        return context
    
def checking_deposit(request):
    user = request.user
    account = CheckingAccount.objects.get(user=user)
    
    if request.method == 'POST':
        form = CheckingDepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            transaction = CheckingTransaction.objects.create(
                account=account,
                transaction_type='D',
                amount=amount,
            )
            account.balance += amount
            account.save()
            messages.success(request, f'Deposit of {amount} was successful!')
            return redirect('checking_balance')
    else:
        form = CheckingDepositForm()

    context = {
        'form': form,
        'account': account,
    }
    return render(request, 'main_app/checking_deposit.html', context)

def checking_withdrawal(request):
    user = request.user
    account = CheckingAccount.objects.get(user=user)
    
    if request.method == 'POST':
        form = CheckingWithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if account.balance < amount:
                messages.warning(request, 'Insufficient balance to make withdrawal')
            else:
                transaction = CheckingTransaction.objects.create(
                    account=account,
                    transaction_type='W',
                    amount=amount,
                )
                account.balance -= amount
                account.save()
                messages.success(request, f'Withdrawal of {amount} was successful!')
                return redirect('checking_balance')
    else:
        form = CheckingWithdrawalForm()

    context = {
        'form': form,
        'account': account,
    }
    return render(request, 'main_app/checking_withdrawal.html', context)

@login_required
def checking_transfers(request):
    if request.method == 'POST':
        sender = CheckingAccount.objects.get(user=request.user)
        receiver = SavingsAccount.objects.get(user=request.user)
        amount = float(request.POST['amount'])
        
        if sender.balance >= amount and amount > 0:
            sender.balance -= amount
            receiver.balance += amount
            sender.save()
            receiver.save()
            
            Transaction.objects.create(
                sender=sender,
                receiver=receiver,
                amount=amount,
            )
            
            context = {
                'success_message': f'You have transferred ${amount:.2f} from your checking account to your savings account.',
            }
        else:
            context = {
                'error_message': 'Invalid transfer amount.',
            }
        
        return render(request, 'main_app/checking_transfers.html', context)
    else:
        return render(request, 'main_app/checking_transfers.html')

@login_required
def checking_withdrawal(request):
    if request.method == 'POST':
        checking_account = CheckingAccount.objects.get(user=request.user)
        amount = float(request.POST['amount'])
        
        if checking_account.balance >= amount and amount > 0:
            checking_account.balance -= amount
            checking_account.save()
            
            Transaction.objects.create(
                checking_account=checking_account,
                amount=amount,
            )
            
            context = {
                'success_message': f'You have withdrawn ${amount:.2f} from your checking account.',
            }
        else:
            context = {
                'error_message': 'Invalid withdrawal amount.',
            }
        
        return render(request, 'main_app/checking_withdrawal.html', context)
    else:
        return render(request, 'main_app/checking_withdrawal.html')
