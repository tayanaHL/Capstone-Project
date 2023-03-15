from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models_customs import CustomUser


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='First name')
    last_name = forms.CharField(max_length=30, required=True, label='Last name')
    email = forms.EmailField(required=True, label='Email')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'autofocus': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = forms.CharField(label='Email', max_length=255)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).count() == 0:
            raise forms.ValidationError("This email address is not registered.")
        return email

