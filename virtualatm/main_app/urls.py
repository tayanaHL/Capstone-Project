from django.urls import path
from . import views

urlpatterns = [
    path('checking/', views.checking, name='checking'),
    path('savings/', views.savings, name='savings'),
    path('checking_balance/', views.CheckingBalanceView.as_view(), name='checking_balance'),
    path('savings_balance/', views.SavingsBalanceView.as_view(), name='savings_balance'),
    path('checking_transaction/', views.checking_transaction, name='checking_transaction'),
    path('savings_transaction/', views.savings_transaction, name='savings_transaction'),
]

    


