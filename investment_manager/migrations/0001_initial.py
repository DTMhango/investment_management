# Generated by Django 5.0.6 on 2024-06-20 15:36

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('client_nrc', models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(message='NRC must be in the format 123456/78/9', regex='^\\d{6}/\\d{2}/\\d$')])),
                ('investment_type', models.CharField(choices=[('lump_sum', 'Lump Sum'), ('regular_contribution', 'Regular Contribution')], max_length=50)),
                ('date_of_birth', models.DateField()),
                ('risk_level', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], max_length=10)),
                ('financial_goal', models.CharField(choices=[('education', 'Education'), ('retirement', 'Retirement'), ('emergency_fund', 'Emergency Fund'), ('home_ownership', 'Home Ownership'), ('business', 'Business')], max_length=50)),
                ('investment_duration', models.IntegerField()),
                ('start_date', models.DateTimeField()),
                ('maturity_date', models.DateTimeField(blank=True, null=True)),
                ('monthly_contribution', models.DecimalField(decimal_places=2, max_digits=10)),
                ('target_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(choices=[('usd', 'USD'), ('zmw', 'ZMW')], max_length=3)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
