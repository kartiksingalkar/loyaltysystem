from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Shop(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    loyalty_points = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    points_balance = models.IntegerField(default=0)
    active_points = models.IntegerField(default=0)
    expired_points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class LoyaltyPoint(models.Model):
    STATUS_CHOICES = [
        ('EARNED', 'Earned'),
        ('ACTIVE', 'Active'),
        ('REDEEMED', 'Redeemed'),
        ('EXPIRED', 'Expired'),
    ]

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    points = models.IntegerField()
    date_earned = models.DateTimeField(auto_now_add=True)
    activation_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='EARNED')
    redeemed_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.customer.user.username} - {self.points} points"

class PointTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('EARN', 'Earn'),
        ('REDEEM', 'Redeem'),
    ]

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    bill_no = models.CharField(max_length=50)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2)
    points_earned = models.IntegerField(default=0)
    points_redeemed = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    merchant_id = models.ForeignKey(Shop, related_name='merchant_transactions', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)

    def __str__(self):
        return f"{self.customer.user.username} - {self.transaction_type} - {self.points_earned if self.transaction_type == 'EARN' else self.points_redeemed} points"

class Redemption(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    points_used = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
    points_detail = models.JSONField()

    def __str__(self):
        return f"{self.customer.user.username} - {self.points_used} points redeemed"
