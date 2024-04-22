from django.core.checks import messages
from django.shortcuts import render

from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm


# Create your views here.

@login_required
def home(request):

    return render(request, 'register/home.html')


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # You can add a redirect to login page or wherever you want
            return redirect(reverse('login'))
    else:
        form = SignUpForm()
    return render(request, 'register/register.html', {'form': form})


class UserLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'register/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('home')


class LogoutViewGET(LogoutView):
    next_page = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if 'update_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('edit_profile')

        # Inside the view function
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important!
                # messages.success(request, 'Your password was successfully updated!')
                print('Your password was successfully updated!')
                return redirect('edit_profile')
            else:
                print('Please correct the error below.')
                messages.error(request, 'Please correct the error below.')
        else:
            password_form = PasswordChangeForm(request.user)
    else:
        profile_form = ProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'register/edit_profile.html', context)
