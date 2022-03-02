# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from accounts.models import Account
from carts.models import Product, Variation


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, db_column='user',verbose_name='付款人email')
    payment_id = models.CharField(max_length=100,verbose_name='paypalID')
    payment_method = models.CharField(max_length=100,verbose_name='付款形式')
    amount_paid = models.CharField(max_length=100,verbose_name='付款金額')
    status = models.CharField(max_length=100,verbose_name='付款狀態')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id

    class Meta:
        managed = False
        db_table = 'b2c_features\".\"Payment'


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, db_column='user', null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, db_column='payment', blank=True, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True, null=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(max_length=20, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def full_address(self):
        return '{} {}'.format(self.address_line_1, self.address_line_2)

    def __str__(self):
        return self.first_name

    class Meta:
        managed = False
        db_table = 'b2c_features\".\"Order'


class Orderproduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, db_column='payment', blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, db_column='user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product')
    variation = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name

    class Meta:
        managed = False
        db_table = 'b2c_features\".\"OrderProduct'
