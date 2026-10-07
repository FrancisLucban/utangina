from django import forms
from .models import Debt, Payment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)

class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['person_name', 'phone_number', 'debt_type', 'amount', 'description', 'date_set', 'due_date']
        widgets = {
            'date_set': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Debt amount must be greater than zero.")

        if self.instance and self.instance.pk:
            total_paid = sum(p.amount for p in self.instance.payments.all())
            if amount is not None and amount < total_paid:
                raise forms.ValidationError(
                    f"Debt amount cannot be less than ₱{total_paid} already paid."
                )

        return amount

    def clean_person_name(self):
        name = self.cleaned_data.get('person_name', '').strip()
        if not name:
            raise forms.ValidationError("Person name cannot be blank or just spaces.")
        return name

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get('due_date')
        date_set = cleaned_data.get('date_set')
        if due_date and date_set and due_date < date_set:
            raise forms.ValidationError("Due date cannot be earlier than the date the debt was set.")
        return cleaned_data


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'date_paid', 'note']
        widgets = {
            'date_paid': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, debt=None, **kwargs):
        self.debt = debt
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None:
            return amount
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        if self.debt and amount > self.debt.amount_remaining:
            raise forms.ValidationError(
                f"Payment cannot exceed the remaining balance of ₱{self.debt.amount_remaining}."
            )
        return amount