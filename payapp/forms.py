from django import forms
from django.core.validators import MinValueValidator
from decimal import Decimal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

CURRENCY_CHOICES = [
    ('USD', 'US Dollars'),
    ('GBP', 'British Pounds'),
    ('EUR', 'Euros'),
]


class PaymentForm(forms.Form):
    recipient_email = forms.EmailField(label='Recipient Email')
    sender_currency = forms.CharField(widget=forms.HiddenInput())
    amount = forms.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        initial=Decimal('0.00'),
        label='You send'
    )
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, label='Currency of Transaction')
    recipient_amount = forms.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        initial=Decimal('0.00'),
        label='They receive'
    )
    note = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        sender_currency = kwargs.pop('sender_currency', None)
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['sender_currency'].initial = sender_currency
        self.fields['amount'].label = f'You send (in {sender_currency})'
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'recipient_email',
            'note',
            Field('sender_currency', type="hidden"),
            Field('currency', css_class="form-control"),
            Field('recipient_amount', css_class="form-control"),
            Field('amount', readonly=True, css_class="form-control"),
            FormActions(
                Submit('submit', 'Send Payment', css_class='btn-primary')
            )
        )


class ReceivePaymentForm(forms.Form):
    recipient_email = forms.EmailField(label='Recipient Email')
    receive_amount = forms.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        label='You Receive'
    )
    receive_currency = forms.ChoiceField(choices=CURRENCY_CHOICES, label='Receive Currency')
    note = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ReceivePaymentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'recipient_email',
            'note',
            Field('receive_amount', css_class="form-control", autofocus=True),
            Field('receive_currency', css_class="form-control"),
            FormActions(
                Submit('submit', 'Receive Payment', css_class='btn-primary')
            )
        )
