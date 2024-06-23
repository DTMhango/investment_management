from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date
from decimal import Decimal


# Create your models here.
class Client(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=50)
    date_of_joining = models.DateField()
    client_nrc = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^\d{6}/\d{2}/\d$',
                message='NRC must be in the format 123456/78/9'
            )
        ],
        unique=True
    )
    contribution_type = models.CharField(
        max_length=50,
        choices=[('lump_sum', 'Lump Sum'), ('regular_contribution', 'Regular Contribution')]
    )
    contribution_frequency = models.CharField(
        max_length=50,
        choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('semi-annual', 'Semi-Annual'), ('annual', 'Annual')]
    )
    date_of_birth = models.DateField()
    risk_level = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    )
    financial_goal = models.CharField(
        max_length=50,
        choices=[('education', 'Education'), ('retirement', 'Retirement'), ('emergency_fund', 'Emergency Fund'), ('home_ownership', 'Home Ownership'), ('business', 'Business')]
    )
    # investment_duration = models.IntegerField()
    # maturity_date = models.DateField(null=True, blank=True)
    expected_monthly_contribution = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(
        max_length=3,
        choices=[('usd', 'USD'), ('zmw', 'ZMW')]
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        valid_frequencies = [choice[0] for choice in self._meta.get_field('contribution_frequency').choices]
        if self.contribution_frequency not in valid_frequencies:
            self.contribution_frequency = 'lump_sum'
        super(Client, self).save(*args, **kwargs)

    def total_contributions(self):
        return self.contribution_set.aggregate(total=models.Sum('amount'))['total'] or 0
    
    def total_investments(self):
        return self.investment_set.aggregate(total=models.Sum('investment_amount'))['total'] or 0
    
    def amount_left_for_investment(self):
        return self.total_contributions() - self.total_investments()


class Contribution(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.client.currency.upper()} {self.amount:.2f} Received On: {self.date:%d/%m/%Y}"


class Investment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    investment_duration = models.IntegerField()
    start_date = models.DateField()
    maturity_date = models.DateField(null=True, blank=True)
    investment_type = models.CharField(
        max_length=50,
        choices=[
            ('fd', 'Fixed Deposit'), 
            ('bond', 'Government Bond'), 
            ('t_bill', 'Treasury Bill'), 
            ('abc_bf', 'ABC Balanced Fund'),
            ('abc_ef', 'ABC Equity Fund'),
            ('abc_mmf', 'ABC Money Market Fund'),
            ('abc_usdf', 'ABC USD Fund'),
            ('abc_usd_hyf', 'ABC USD High-Yield Fund'),
            ('abc_zmw_hyf', 'ABC ZMW High-Yield Fund'),
            ('mpile_bf', 'Mpile Balanced Fund'),
            ('mpile_gf', 'Mpile Gratuity Fund'),
            ('mpile_hydf', 'Mpile High-Yield Debt Fund'),
            ('mpile_lef', 'Mpile Local Equity Fund'),
            ('mpile_mmf', 'Mpile Money Market Fund'),
            ('mpile_osef', 'Mpile Offshore Equity Fund'),
            ('mpile_pf', 'Mpile Property Fund'),
        ]
    )
    investment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    expected_annual_growth_rate = models.DecimalField(max_digits=5, decimal_places=4)
    expected_current_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def clean(self):
        if self.client.amount_left_for_investment() < self.investment_amount:
            raise ValidationError(
                f"The investment amount of {self.client.currency.upper()} {self.investment_amount:2f} exceeds the amount left for investment for the client ({self.client.currency.upper()} {self.client.amount_left_for_investment()})"
            )

    def save(self, *args, **kwargs):
        if not self.maturity_date:
            self.maturity_date = self.start_date + relativedelta(months=self.investment_duration)

        self.full_clean()  # Validate the model instance

        # Calculate the expected current value based on the elapsed time
        if date.today() > self.maturity_date:
            days_elapsed = (self.maturity_date - self.start_date).days
        else:
            days_elapsed = (date.today() - self.start_date).days
        years_elapsed = Decimal(days_elapsed) / Decimal('365.25')  # Approximate number of days in a year including leap years
        self.expected_current_value = self.investment_amount * (Decimal('1') + self.expected_annual_growth_rate) ** years_elapsed
        super(Investment, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.client.currency.upper()} {self.investment_amount:.2f} Invested On: {self.start_date:%d/%m/%Y}"