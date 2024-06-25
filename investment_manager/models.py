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

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=50)
    date_of_birth = models.DateField()
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
    date_of_joining = models.DateField() 
    risk_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'), 
            ('medium', 'Medium'), 
            ('high', 'High')
        ]
    )
    contribution_type = models.CharField(
        max_length=50,
        choices=[
            ('lump_sum', 'Lump Sum'), 
            ('regular_contribution', 'Regular Contribution')
        ]
    )
    contribution_frequency = models.CharField(
        max_length=50,
        choices=[
            ('monthly', 'Monthly'), 
            ('quarterly', 'Quarterly'), 
            ('semi-annual', 'Semi-Annual'), 
            ('annual', 'Annual'), 
            ('once_off', 'Once-Off')
        ]
    )
    financial_goal = models.CharField(
        max_length=50,
        choices=[
            ('education', 'Education'), 
            ('retirement', 'Retirement'), 
            ('emergency_fund', 'Emergency Fund'), 
            ('home_ownership', 'Home Ownership'), 
            ('business', 'Business')
        ]
    )
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    expected_contribution = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(
        max_length=3,
        choices=[('usd', 'USD'), ('zmw', 'ZMW')]
    )
    manager = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def format_target(self):
        return f"{self.target_amount:,.2f}"
    
    def format_contribution(self):
        return f"{self.expected_contribution:,.2f}"

    def get_manager_full_name(self):
        return f"{self.manager.first_name} {self.manager.last_name}"

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.contribution_type == 'lump_sum':
            self.contribution_frequency = 'once_off'
        super(Client, self).save(*args, **kwargs)

    def total_contributions(self):
        return self.contribution_set.aggregate(total=models.Sum('investable_amount'))['total'] or 0
    
    def total_investments(self):
        return self.investment_set.aggregate(total=models.Sum('investment_amount'))['total'] or 0
    
    def amount_left_for_investment(self):
        return self.total_contributions() - self.total_investments()


class Contribution(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField()
    contribution_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=50, 
        choices=[
            ('cash', 'Cash'), 
            ('ddacc', 'DDACC'), 
            ('mobile_money', 'Mobile Money'), 
            ('bank_transfer', 'Bank Transfer'), 
            ('cheque', 'Cheque')
        ]
    )
    fee_rate_percentage = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, default=Decimal('3.000'))
    fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    investable_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    description = models.TextField(null=True, blank=True)  # Optional field for additional context

    def get_manager_full_name(self):
        return f"{self.manager.first_name} {self.manager.last_name}"

    def save(self, *args, **kwargs):
        self.fees = self.contribution_amount * Decimal(self.fee_rate_percentage) / 100
        self.investable_amount = self.contribution_amount - self.fees
        super(Contribution, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.client.currency.upper()} {self.contribution_amount:,.2f} Received On: {self.date:%d/%m/%Y}"


class Investment(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
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
    expected_annual_growth_rate_percentage = models.DecimalField(max_digits=5, decimal_places=3)
    expected_current_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)  # Optional field for additional context
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('completed', 'Completed')], default='active')

    def get_manager_full_name(self):
        return f"{self.manager.first_name} {self.manager.last_name}"

    def clean(self):
        if self.client.amount_left_for_investment() < self.investment_amount:
            raise ValidationError(
                f"The investment amount of {self.client.currency.upper()} {self.investment_amount:.2f} exceeds the amount left for investment for the client ({self.client.currency.upper()} {self.client.amount_left_for_investment():.2f})"
            )

    def save(self, *args, validate=True, **kwargs):
        if not self.maturity_date:
            self.maturity_date = self.start_date + relativedelta(months=self.investment_duration)

        if validate:
            self.full_clean()  # Validate the model instance

        # Calculate the expected current value based on the elapsed time
        if date.today() > self.maturity_date:
            days_elapsed = (self.maturity_date - self.start_date).days
        else:
            days_elapsed = (date.today() - self.start_date).days
        years_elapsed = Decimal(days_elapsed) / Decimal('365.25')  # Approximate number of days in a year including leap years
        self.expected_current_value = self.investment_amount * (Decimal('1') + self.expected_annual_growth_rate_percentage / 100) ** years_elapsed

        # Update status based on maturity date
        if date.today() > self.maturity_date:
            self.status = 'completed'
        else:
            self.status = 'active'

        super(Investment, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.client.currency.upper()} {self.investment_amount:.2f} Invested On: {self.start_date:%d/%m/%Y}"