# Generated by Django 5.0.6 on 2024-06-27 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loyaltyapp', '0007_alter_pointtransaction_bill_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='expiration_date',
            field=models.DateField(),
        ),
    ]
