# Generated by Django 5.0.6 on 2024-06-27 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loyaltyapp', '0003_loyaltypoint_non_expiry_purchase_item_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='merchant_id',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
