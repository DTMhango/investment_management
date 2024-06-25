from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Client, Contribution, Investment


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}), max_length=50)
    last_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}), max_length=50)
    email = forms.EmailField(label="", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args: Any, **kwargs: Any):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class CreateClientForm(forms.ModelForm):
    full_name = forms.CharField(
        required=True, 
        label="", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name: First (Middle) Last'}),
        max_length=100
    )
    email = forms.EmailField(
        required=True, 
        label="", 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    phone = forms.CharField(
        required=True, 
        label="", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        max_length=15
    )
    city = forms.CharField(
        required=True, 
        label="", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
        max_length=50
    )
    date_of_birth = forms.DateField(
        required=True, 
        label="", 
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Date Of Birth: YYYY-MM-DD'})
    )
    client_nrc = forms.CharField(
        required=True, 
        label="", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NRC Number'}),
        max_length=50
    )
    date_of_joining = forms.DateField(
        required=True, 
        label="", 
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Date Of Joining: YYYY-MM-DD'})
    )
    risk_level = forms.ChoiceField(
        choices=Client._meta.get_field('risk_level').choices, 
        required=True, 
        label="", 
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Risk Tolerance e.g., "Low", "Medium" or "High"'})
    )
    contribution_type = forms.ChoiceField(
        choices=Client._meta.get_field('contribution_type').choices, 
        required=True, 
        label="", 
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Method of Contribution e.g., "Regular Contribution" or "Lump Sum"'})
    )
    contribution_frequency = forms.ChoiceField(
        choices=Client._meta.get_field('contribution_frequency').choices, 
        required=True, 
        label="", 
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Contribution Frequency e.g., "Monthly", "Quarterly", "Semi-Annual", "Annual" or "Once-Off"'})
    )
    financial_goal = forms.ChoiceField(
        choices=Client._meta.get_field('financial_goal').choices, 
        required=True, 
        label="", 
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Client\'s Financial Goal e.g., "Education", "Retirement", "Emergency Fund", "Home Ownership", "Business"'})
    )
    target_amount = forms.DecimalField(
        required=True, 
        label="", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Client Target Amount'})
    )
    expected_contribution = forms.DecimalField(
        required=True, 
        label="", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Expected (Periodic) Contribution Amount'})
    )
    currency = forms.ChoiceField(
        choices=Client._meta.get_field('currency').choices, 
        label="", 
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': '"USD" or "ZMW"'})
    )
    
    class Meta:
        model = Client
        exclude = ("user",)


class CreateContributionForm(forms.ModelForm):
    date = forms.DateField(
        required=True, 
        label="", 
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Date: YYYY-MM-DD'})
    )
    contribution_amount = forms.DecimalField(
        required=True, 
        label="", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contribution Amount'})
    )
    payment_method = forms.ChoiceField(
        choices=Contribution._meta.get_field('payment_method').choices, 
        required=True, 
        label="", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fee_rate_percentage = forms.DecimalField(
        required=True, 
        label="", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fee Rate Percentage'})
    )
    description = forms.CharField(
        required=False, 
        label="", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'})
    )


    def __init__(self, *args, **kwargs):
        client_id = kwargs.pop('client_id', None)
        super(CreateContributionForm, self).__init__(*args, **kwargs)
        if client_id:
            self.instance.client_id = client_id


    class Meta:
        model = Contribution
        exclude = ("client", "manager", "created_at", "fees", "investable_amount")


class CreateInvestmentForm(forms.ModelForm):
    investment_duration = forms.IntegerField(
        required=True, 
        label="", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Investment Duration (months)'})
    )
    start_date = forms.DateField(
        required=True, 
        label="", 
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Start Date: YYYY-MM-DD'})
    )
    investment_type = forms.ChoiceField(
        choices=Investment._meta.get_field('investment_type').choices, 
        required=True, 
        label="", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    investment_amount = forms.DecimalField(
        required=True, 
        label="", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Investment Amount'})
    )
    expected_annual_growth_rate_percentage = forms.DecimalField(
        required=True, 
        label="", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Expected Annual Growth Rate (%)'})
    )
    description = forms.CharField(
        required=False, 
        label="", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'})
    )

    def __init__(self, *args, **kwargs):
        client_id = kwargs.pop('client_id', None)
        super(CreateInvestmentForm, self).__init__(*args, **kwargs)
        if client_id:
            self.instance.client_id = client_id


    class Meta:
        model = Investment
        exclude = ("client", "manager", "created_at", "maturity_date", "expected_current_value", "status")

    
