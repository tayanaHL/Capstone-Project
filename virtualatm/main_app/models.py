from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse
from .models_customs import CustomUser
import random, string


# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user


    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(unique=True)
#     first_name = models.CharField(_('first name'), max_length=30, blank=True)
#     last_name = models.CharField(_('last name'), max_length=30, blank=True)
#     is_active = models.BooleanField(_('active'), default=True)
#     is_staff = models.BooleanField(_('staff status'), default=False)
#     date_joined = models.DateTimeField(default=timezone.now, verbose_name='date joined')

    # # objects = CustomUserManager()

    # USERNAME_FIELD = 'email'
    # EMAIL_FIELD = 'email'
    # REQUIRED_FIELDS = []

    # class Meta:
    #     verbose_name = _('user')
    #     verbose_name_plural = _('users')

    # def __str__(self):
    #     return self.email

class Card(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    number = models.CharField(max_length=16, unique=True)

    @receiver(post_save, sender=CustomUser)
    def create_card(sender, instance, created, **kwargs):
        from .models import Card
        if created:
            # Generate a random 16-digit number for the card
            card_number = ''.join(random.choices(string.digits, k=16))
            # Create a new Card instance for the user with the generated card number
            Card.objects.create(user=instance, number=card_number)



class CheckingAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=8, decimal_places=2)

def get_absolute_url(self):
    return reverse('checking_balance', kwargs={'account_id': self.id})
    
class SavingsAccount(models.Model):
    
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

def get_absolute_url(self):
    return reverse('savings_balance', kwargs={'account_id': self.id})

class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)


class CheckingBalance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class SavingsBalance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class CheckingDeposit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

   
class SavingsDeposit(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class CheckingWithdrawal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class CheckingTransaction(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class CheckingTransfer(models.Model):
    from_account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checking_transfers_sent')
    to_account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checking_transfers_received')
amount = models.DecimalField(max_digits=10, decimal_places=2)

class SavingsTransaction(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class SavingsTransfer(models.Model):
    from_account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='savings_transfers_sent')
    to_account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='savings_transfers_received')


class SavingsWithdrawal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    