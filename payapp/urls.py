from django.urls import path
from . import views


urlpatterns = [
    path('send-payment/', views.send_payment, name='send_payment'),
    path('request-payment/', views.request_payment, name='request_payment'),
    path('transactions/', views.view_transactions, name='view_transactions'),
    path('conversion/<str:currency1>/<str:currency2>/<str:amount>', views.convert_currency, name='convert_currency'),
    path('notifications/', views.fetch_notifications, name='fetch_notifications'),
    path('fetch-balance/', views.fetch_balance, name='fetch_balance'),
    path('transactions/approve/<int:transaction_id>/', views.approve_transaction, name='approve_transaction'),
    path('transactions/reject/<int:transaction_id>/', views.reject_transaction, name='reject_transaction')
]
