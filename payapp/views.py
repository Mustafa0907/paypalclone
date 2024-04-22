from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from .models import Transaction
from register.models import ExtendedUser
from .forms import PaymentForm, ReceivePaymentForm
from django.http import JsonResponse, HttpResponseBadRequest
import requests
from decimal import Decimal
from django.db import transaction as db_transaction


def convert_currency_api(from_currency, to_currency, amount):
    # Assuming your currency conversion service is running locally
    response = requests.get(f'http://localhost:8000/conversion/{from_currency}/{to_currency}/{amount}')
    if response.status_code == 200:
        return response.json()['converted_amount']
    else:
        return None


@login_required
def send_payment(request):
    sender_id = request.user.id  # Get the user ID

    # Retrieve the ExtendedUser instance for the sender
    sender = ExtendedUser.objects.get(id=sender_id)

    sender_currency = sender.currency
    print(sender_currency + "hello")
    if request.method == 'POST':
        form = PaymentForm(request.POST, sender_currency=sender_currency)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            amount = form.cleaned_data['amount']
            transaction_currency = form.cleaned_data['currency']
            note = form.cleaned_data['note']
            recipient_amount = form.cleaned_data['recipient_amount']

            try:
                recipient = ExtendedUser.objects.get(email=recipient_email)

                if transaction_currency != recipient.currency:
                    converted_amount = convert_currency_api(transaction_currency, recipient.currency, recipient_amount)
                    if converted_amount is None:
                        messages.error(request, 'Currency conversion error.')
                        return render(request, 'payapp/send_payment.html', {'form': form})
                else:
                    converted_amount = recipient_amount

                # Convert amount from sender's currency to the transaction currency for balance check
                if transaction_currency != sender_currency:
                    amount_in_sender_currency = convert_currency_api(transaction_currency, sender_currency,
                                                                     recipient_amount)
                else:
                    amount_in_sender_currency = recipient_amount

                if amount_in_sender_currency is None:
                    messages.error(request, 'Currency conversion error for sender.')
                    return render(request, 'payapp/send_payment.html', {'form': form})

                if sender.balance >= amount_in_sender_currency:
                    with transaction.atomic():
                        amount_in_sender_currency = Decimal(amount_in_sender_currency)
                        sender.balance -= amount_in_sender_currency
                        recipient.balance += Decimal(converted_amount)
                        sender.save()
                        recipient.save()

                        Transaction.objects.create(
                            transaction_type='SEND',
                            amount=recipient_amount,
                            # Store the transaction in the amount the sender wants the recipient to receive
                            sender=sender,
                            recipient=recipient,
                            currency=transaction_currency,  # Store in the transaction currency
                            status='COMPLETED',
                            note=note,
                            is_notified=False
                        )

                        messages.success(request, 'Payment successful!')
                        return redirect('send_payment')
                else:
                    messages.error(request, 'Insufficient balance.')
            except ExtendedUser.DoesNotExist:
                messages.error(request, 'Recipient not found.')
    else:
        # Instantiate the form with the sender's currency on GET request
        form = PaymentForm(sender_currency=sender_currency)
    return render(request, 'payapp/send_payment.html', {
        'form': form,
        'sender_currency': sender_currency,
    })


# @login_required
# def request_payment(request):
#     if request.method == 'POST':
#         form = PaymentForm(request.POST)  # Assuming the PaymentForm can be reused or adjusted for payment requests
#         if form.is_valid():
#             recipient_email = form.cleaned_data['recipient_email']
#             amount = form.cleaned_data['amount']
#             note = form.cleaned_data['note']
#             sender_id = request.user.id  # Get the user ID
#
#             sender = ExtendedUser.objects.get(id=sender_id)
#             try:
#                 recipient = ExtendedUser.objects.get(email=recipient_email)
#
#                 Transaction.objects.create(
#                     transaction_type='REQUEST',
#                     amount=amount,
#                     sender=sender,
#                     recipient=recipient,
#                     currency=sender.currency,
#                     status='PENDING',  # Assuming requests start as 'PENDING'
#                     note=note,
#                     is_notified=False  # Since this is a new request, notification is initially not sent
#                 )
#
#                 messages.success(request, 'Payment request sent successfully.')
#                 return redirect('request_payment')
#             except ExtendedUser.DoesNotExist:
#                 messages.error(request, 'Recipient not found.')
#     else:
#         form = PaymentForm()
#     return render(request, 'payapp/request_payment.html', {'form': form})


@login_required
def request_payment(request):
    sender_id = request.user.id  # Get the user ID

    # Retrieve the ExtendedUser instance for the sender
    sender = ExtendedUser.objects.get(id=sender_id)

    if request.method == 'POST':
        form = ReceivePaymentForm(request.POST)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            receive_amount = form.cleaned_data['receive_amount']
            note = form.cleaned_data['note']
            transaction_currency = form.cleaned_data['receive_currency']

            try:
                recipient = ExtendedUser.objects.get(email=recipient_email)
                Transaction.objects.create(
                    transaction_type='REQUEST',
                    amount=receive_amount,
                    sender=sender,
                    recipient=recipient,
                    currency=transaction_currency,
                    status='PENDING',
                    note=note,
                    is_notified=False
                )

                messages.success(request, 'Payment request sent successfully.')
                return redirect('request_payment')  # Redirect to the same or another view as appropriate
            except ExtendedUser.DoesNotExist:
                messages.error(request, 'Recipient not found.')
    else:
        form = ReceivePaymentForm()

    return render(request, 'payapp/request_payment.html', {'form': form})


@login_required
def view_transactions(request):
    # Fetch all transactions related to the current user, both sent and received
    sent_transactions = Transaction.objects.filter(sender=request.user)
    received_transactions = Transaction.objects.filter(recipient=request.user)

    # Update all fetched transactions where is_notified is False to True
    Transaction.objects.filter(sender=request.user, is_notified=False).update(is_notified=True)
    Transaction.objects.filter(recipient=request.user, is_notified=False).update(is_notified=True)

    # Context to pass to the template
    context = {
        'sent_transactions': sent_transactions,
        'received_transactions': received_transactions,
    }

    # Render the template with the context
    return render(request, 'payapp/view_transactions.html', context)


EXCHANGE_RATES = {
    'USD': {
        'GBP': 0.80,
        'EUR': 0.94,
        'USD': 1.00,
    },
    'GBP': {
        'USD': 1.25,
        'EUR': 1.17,
        'GBP': 1.00,
    },
    'EUR': {
        'USD': 1.07,
        'GBP': 0.86,
        'EUR': 1.00,
    },
}


def convert_currency(request, currency1, currency2, amount):
    try:
        amount = float(amount)
        if currency1 in EXCHANGE_RATES and currency2 in EXCHANGE_RATES[currency1]:
            rate = EXCHANGE_RATES[currency1][currency2]
            converted_amount = rate * amount
            print('converted: ')
            print(converted_amount)
            return JsonResponse({'converted_amount': converted_amount})
        else:
            return HttpResponseBadRequest("One or both of the provided currencies are not supported.")
    except ValueError:
        return HttpResponseBadRequest("Invalid amount provided.")


@login_required
def fetch_notifications(request):
    notifications = Transaction.objects.filter(
        recipient=request.user,
        is_notified=False
    ).order_by('-created_at')[:10]
    # notifications.update(is_notified=True)  # Optionally mark them as read

    data = [{
        'sender': notification.sender.username,  # Ensure sender has a username attribute
        'amount': str(notification.amount),
        'currency': notification.currency,
        'transaction_type': notification.transaction_type
    } for notification in notifications]

    return JsonResponse({'notifications': data})


@login_required
def fetch_balance(request):
    user_id = request.user.id
    user = ExtendedUser.objects.get(id=user_id)
    # Fetch user balance and currency if ExtendedUser is the user model
    user_balance = user.balance
    user_currency = user.currency

    return JsonResponse({
        'user_balance': str(user_balance),  # Convert Decimal to string for JSON serialization
        'user_currency': user_currency,
    })


@login_required
def approve_transaction(request, transaction_id):
    print("Entered approve_transaction view")
    try:
        pending_transaction = Transaction.objects.get(id=transaction_id, status='PENDING')
        print(f"Transaction found: {pending_transaction}")

        if pending_transaction.recipient != request.user:
            messages.error(request, "Unauthorized to approve this transaction.")
            return redirect('view_transactions')

        with db_transaction.atomic():
            sender = pending_transaction.sender
            transaction_amount = pending_transaction.amount
            if pending_transaction.currency != sender.currency:
                amount_in_sender_currency = convert_currency_api(pending_transaction.currency, sender.currency,
                                                                 transaction_amount)
                print(f"Converted amount in sender's currency: {amount_in_sender_currency}")
                if amount_in_sender_currency is None:
                    messages.error(request, 'Currency conversion error.')
                    return redirect('view_transactions')
            else:
                amount_in_sender_currency = transaction_amount

            if pending_transaction.currency != pending_transaction.recipient.currency:
                converted_amount = convert_currency_api(pending_transaction.currency,
                                                        pending_transaction.recipient.currency,
                                                        pending_transaction.amount)
                print(f"Converted amount: {converted_amount}")
                if converted_amount is None:
                    messages.error(request, 'Currency conversion error.')
                    return redirect('view_transactions')
            else:
                converted_amount = pending_transaction.amount

            print(
                f"Before update: Status {pending_transaction.status}, Recipient balance {pending_transaction.recipient.balance}")
            pending_transaction.recipient.balance -= Decimal(converted_amount)
            pending_transaction.sender.balance += Decimal(amount_in_sender_currency)
            pending_transaction.recipient.save()
            pending_transaction.sender.save()
            pending_transaction.status = 'APPROVED'
            pending_transaction.save()
            print(
                f"After update: Status {pending_transaction.status}, Recipient balance {pending_transaction.recipient.balance}")

            messages.success(request, 'Transaction approved successfully!')
            return redirect('view_transactions')

    except Transaction.DoesNotExist:
        print('bsdk')
        messages.error(request, 'Transaction not found.')
    except Exception as e:
        print('bsdk2' + str(e))
        messages.error(request, f'Error processing transaction: {str(e)}')

    return redirect('view_transactions')


@login_required
def reject_transaction(request, transaction_id):
    print("Entered reject_transaction view")
    try:
        pending_transaction = Transaction.objects.get(id=transaction_id, status='PENDING')
        print(f"Transaction found: {pending_transaction}")

        if pending_transaction.recipient != request.user:
            messages.error(request, "Unauthorized to reject this transaction.")
            return redirect('view_transactions')

        with db_transaction.atomic():
            # Update the status to REJECTED without altering balances
            pending_transaction.status = 'REJECTED'
            pending_transaction.save()

            print(f"Transaction status updated to REJECTED for transaction ID {pending_transaction.id}")
            messages.success(request, 'Transaction rejected successfully!')
            return redirect('view_transactions')

    except Transaction.DoesNotExist:
        print('Transaction not found')
        messages.error(request, 'Transaction not found.')
    except Exception as e:
        print(f'Error processing transaction: {str(e)}')
        messages.error(request, f'Error processing transaction: {str(e)}')

    return redirect('view_transactions')