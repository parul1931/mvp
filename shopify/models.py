from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.conf import settings
import PIL
from PIL import Image
import time
import os


class AccountType(models.Model):
	type = models.CharField(max_length=10)

	def __str__(self):
		return str(self.type)

class Account(models.Model):
	account = models.ForeignKey(AccountType, on_delete=models.CASCADE)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	emailid = models.EmailField(unique=True)
	password = models.TextField()
	status = models.IntegerField(default=0)
	activation_key = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return str(self.id)

	# def __str__(self):
	# 	return str(self.first_name)


class Vendor(models.Model):
	user = models.OneToOneField(Account, on_delete=models.CASCADE)
	vendor = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return str(self.vendor)


class Categories(models.Model):
	user = models.ForeignKey(AccountType, on_delete=models.CASCADE)
	title = models.CharField(max_length=500)

	def __str__(self):
		return str(self.title)


class Products(models.Model):
	user = models.ForeignKey(Account, on_delete=models.CASCADE)
	category = models.ForeignKey(Categories, on_delete=models.CASCADE)
	title = models.CharField(max_length=500)
	description = models.TextField()
	selling_price = models.FloatField()
	compare_price = models.FloatField()
	is_tax=models.BooleanField(default=False)
	sku = models.CharField(max_length=100)
	barcode=models.CharField(max_length=100)
	created_date=models.DateTimeField(default=timezone.now)
	updated_date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return str(self.id)