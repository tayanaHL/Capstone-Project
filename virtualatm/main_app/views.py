from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models_customs import CustomUser
from .models import CheckingAccount, SavingsAccount, CheckingTransaction, SavingsTransaction, SavingsTransfer, CheckingTransfer, Transaction
from .forms import CustomUserCreationForm, CustomAuthenticationForm
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.generic import TemplateView, View


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
    checking_account = CheckingAccount.objects.filter(user=request.user)

    # Render the checking template with the user's checking account balance
    return render(request, 'checking.html', {'balance': checking_account})

@login_required
def savings(request):
    # Get the savings account for the logged-in user
    user = CustomUser.objects.get(email=request.user.email)
    savings_account = SavingsAccount.objects.filter(user=request.user)

    # Render the savings template with the user's savings account balance
    return render(request, 'savings.html', {'balance': savings_account})

@login_required
def checking_balance(request):
    user = request.user
    try:
        checking_account = CheckingAccount.objects.get(user=user)
        balance = checking_account.balance
    except CheckingAccount.DoesNotExist:
        balance = 0
    return render(request, 'checking_balance.html', {'balance': balance})

def savings_balance(request):
    user = request.user
    try:
        savings_account = SavingsAccount.objects.get(user=user)
        balance = savings_account.balance
    except SavingsAccount.DoesNotExist:
        balance = 0
    context = {'balance': balance}
    return render(request, 'savings_balance.html', context)

@login_required
def savings_transaction(request):
    transactions = SavingsTransaction.objects.filter(account=request.user)
    return render(request, 'savings_transaction.html', {'transactions': transactions})

@login_required
def checking_transaction(request):
    transactions = CheckingTransaction.objects.filter(account=request.user)
    return render(request, 'checking_transaction.html', {'transactions': transactions})

@login_required
def savings_deposits(request):
    deposits = SavingsAccount.objects.filter(account=request.user)
    return render(request, 'savings_deposits.html', {'deposits': deposits})

@login_required
def checking_deposits(request):
    deposits = CheckingAccount.objects.filter(account=request.user)
    return render(request, 'checking_deposits.html', {'deposits': deposits})

@login_required
def savings_transfers(request):
    if request.method == 'POST':
        action = request.POST['action']
        from_account = SavingsAccount.objects.get(user=request.user)
        if action == 'transfer':
            to_account_id = request.POST['to_account']
            to_account = CheckingAccount.objects.get(id=to_account_id)
        else:
            to_account = from_account
        amount = request.POST.get('amount', None)
        custom_amount = request.POST.get('custom_amount', None)
        if amount == 'other_amount':
            amount = custom_amount
        if amount:
            amount = float(amount)
            if action == 'withdrawal':
                amount = -amount
            if from_account.balance + amount < 0:
                return render(request, 'savings_transfers.html', {'error': 'Insufficient funds.'})
            from_account.balance -= amount
            from_account.save()
            to_account.balance += amount
            to_account.save()
            Transaction.objects.create(
                from_account=from_account,
                to_account=to_account,
                amount=amount,
            )
            return redirect('confirmation')
    else:
        return render(request, 'savings_transfers.html')

@login_required
def checking_transfers(request):
    if request.method == 'POST':
        action = request.POST['action']
        from_account = CheckingAccount.objects.get(user=request.user)
        if action == 'transfer':
            to_account_id = request.POST['to_account']
            to_account = SavingsAccount.objects.get(id=to_account_id)
        else:
            to_account = from_account
        amount = request.POST.get('amount', None)
        custom_amount = request.POST.get('custom_amount', None)
        if amount == 'other_amount':
            amount = custom_amount
        if amount:
            amount = float(amount)
            if action == 'withdrawal':
                amount = -amount
            if from_account.balance + amount < 0:
                return render(request, 'checking_transfers.html', {'error': 'Insufficient funds.'})
            from_account.balance -= amount
            from_account.save()
            to_account.balance += amount
            to_account.save()
            Transaction.objects.create(
                from_account=from_account,
                to_account=to_account,
                amount=amount,
            )
            return redirect('confirmation')
    else:
        return render(request, 'checking_transfers.html')

@login_required
def savings_withdrawal(request):
    savings_account = SavingsAccount.objects.get(account=request.user)
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        if amount <= savings_account.balance:
            savings_account.balance -= amount
            savings_account.save()
            Transaction.objects.create(account=savings_account, description='Withdrawal', amount=amount)
            return redirect('savings_transaction')
        else:
            error_message = 'Insufficient funds'
    else:
        error_message = None
    return render(request, 'savings_withdrawal.html', {'savings_account': savings_account, 'error_message': error_message})

@login_required
def checking_withdrawal(request):
    checking_account = CheckingAccount.objects.get(account=request.user)
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        if amount <= checking_account.balance:
            checking_account.balance -= amount
            checking_account.save()
            Transaction.objects.create(account=checking_account, description='Withdrawal', amount=amount)
            return redirect('checking_transaction')
        else:
            error_message = 'Insufficient funds'
    else:
        error_message = None
    return render(request, 'checking_withdrawal.html', {'checking_account': checking_account, 'error_message': error_message})

def transaction_history(request):
    checking_account = CheckingAccount.objects.get(user=request.user)
    savings_account = SavingsAccount.objects.get(user=request.user)
    checking_transactions = Transaction.objects.filter(
        from_account=checking_account) | Transaction.objects.filter(to_account=checking_account)
    savings_transactions = Transaction.objects.filter(
        from_account=savings_account) | Transaction.objects.filter(to_account=savings_account)
    all_transactions = checking_transactions | savings_transactions
    context = {
        'checking_transactions': checking_transactions,
        'savings_transactions': savings_transactions,
        'all_transactions': all_transactions,
    }
    return render(request, 'transaction_history.html', context)


def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if request.method == 'GET':
        # Render a confirmation page asking the user if they want to delete the transaction
        context = {'transaction': transaction}
        return render(request, 'delete_transaction_confirm.html', context)
    elif request.method == 'POST':
        # Delete the transaction and update the account balance accordingly
        if transaction.from_account:
            transaction.from_account.balance += transaction.amount
            transaction.from_account.save()
        if transaction.to_account:
            transaction.to_account.balance -= transaction.amount
            transaction.to_account.save()
        transaction.delete()
        return redirect('transaction_history')