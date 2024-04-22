
from django.urls import path
from . import views
from .views import UserLoginView, LogoutViewGET
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutViewGET.as_view(), name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]
