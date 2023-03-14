from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models_customs import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['email', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'autofocus': True}))

    class Meta:
        model = CustomUser
        fields = ['email', 'password']
