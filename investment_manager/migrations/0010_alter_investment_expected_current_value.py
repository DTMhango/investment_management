# Generated by Django 5.0.6 on 2024-06-23 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment_manager', '0009_rename_investment_type_client_contribution_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investment',
            name='expected_current_value',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]