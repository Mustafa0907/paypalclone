from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import ExtendedUser


User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    currency = forms.ChoiceField(choices=User.CURRENCY_CHOICES, help_text='Choose your account currency.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'currency')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.currency = self.cleaned_data['currency']  # Ensure currency is saved
        if commit:
            user.save()
        return user


class ProfileForm(UserChangeForm):
    password = None  # Exclude the password field

    class Meta(UserChangeForm.Meta):
        model = ExtendedUser
        fields = ('username', 'email', 'first_name', 'last_name', 'currency')
        widgets = {
            'username': forms.TextInput(attrs={'readonly': True}),
            'email': forms.EmailInput(attrs={'readonly': True}),
        }
