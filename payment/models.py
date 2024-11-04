from django.db import models
from django.contrib.auth.models import User
from shop.models import Product
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime


class ShippingAddress(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	shipping_full_name = models.CharField(max_length=255)
	shipping_email = models.CharField(max_length=255)
	shipping_address1 = models.CharField(max_length=255)
	shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
	shipping_city = models.CharField(max_length=255)
	shipping_region = models.CharField(max_length=255)
	shipping_postcode = models.CharField(max_length=255)
	shipping_country = models.CharField(max_length=255)

	# Don't Pluralise address
	class Meta:
		verbose_name_plural = 'Shipping Address'

	def __str__(self):
		return f'Shipping Address - {str(self.id)}'


# create user Shipping Address by default
def create_shipping(sender, instance, created, **kwargs):
	if created:
		user_shipping = ShippingAddress(user=instance)
		user_shipping.save()

# automate profile

post_save.connect(create_shipping, sender=User)


# create order model


class Order(models.Model):
	# Foreign Key
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	# keys
	full_name = models.CharField(max_length=250)
	email = models.EmailField(max_length=250)
	shipping_address = models.TextField(max_length=15000)
	amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
	date_ordered = models.DateTimeField(auto_now_add=True)
	shipped = models.BooleanField(default=False)
	date_shipped = models.DateTimeField(blank=True, null=True)
	payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
	paid = models.BooleanField(default=False)
	
	def __str__(self):
		return f'Order - {str(self.id)} | Shipped - {self.shipped}'

# Auto add shipping date
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
	if instance.pk:
		now = datetime.datetime.now()
		obj = sender._default_manager.get(pk=instance.pk)
		if instance.shipped and not obj.shipped:
			instance.date_shipped = now


# create order items model


class OrderItem(models.Model):
	# Foreign Keys
	order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
	product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	# keys
	quantity = models.PositiveBigIntegerField(default=1)
	price = models.DecimalField(max_digits=7, decimal_places=2)

	def __str__(self):
		return f'Order Item - {str(self.id)}'
