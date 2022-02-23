# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from store.models import Product, Variation
from accounts.models import Account


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

    class Meta:
        managed = False
        db_table = 'b2c_features\".\"Cart'


class Cartitem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, db_column='user', null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product')
    variation = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, db_column='cart', null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.product

    def sub_total(self):
        return self.product.price * self.quantity

    class Meta:
        managed = False
        db_table = 'b2c_features\".\"CartItem'
