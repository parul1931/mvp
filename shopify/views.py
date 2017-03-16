from django.shortcuts import render, redirect
from forms import LoginForm, RegisterForm, ProductForm
from models import Account, Products,AccountType,Vendor, Categories
from images.models import Images
from django.http import HttpResponse
import hashlib
import random
import json
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from passlib.hash import django_pbkdf2_sha256 as handler
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.core.paginator import Paginator ,PageNotAnInteger,EmptyPage
from shopify.utils.userdetails import UserDetail
import sys

from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView

from django_datatables_view.base_datatable_view import BaseDatatableView

from tables import AccountTable

from table.views import FeedDataView


class AccountDataView(FeedDataView):
	
	token = AccountTable.token

	def get_queryset(self):
		return super(AccountDataView, self).get_queryset().filter(id=1)

def people(request):
	people = AccountTable(Account.objects.filter(account_id=3))
	print "\n\n\n people :    ", people
	return render(request, "table_data.html", {'people': people})


class AccountListJson(BaseDatatableView):
	model = Account

	columns = ['first_name', 'last_name', 'emailid']

	order_columns = ['first_name', 'last_name', '']

	max_display_length = 10

	def render_column(self, row, column):
		if column == "first_name":
			return '{0} {1}'.format(row.first_name, row.last_name)
		else:
			return super(AccountListJson, self).render_column(row, column)

	def filter_queryset(self, qs):
		search = self.request.GET.get(u'search[value]', None)
		if search:
			qs = qs.filter(first_name__isstartswith=search)
		return qs


class AccountsList(ListView):
	model = Account
	context_object_name = "all_accounts"


class CategoryDetailView(DetailView):
	model = Categories

	def get_context_data(self, **kwargs):
		context = super(CategoryDetailView, self).get_context_data(**kwargs)
		products = Products.objects.all()
		context['products_list'] = products
		return context


# class Vendor(TemplateView):
# 	model = Vendor
# 	template_name = "vendor.html"


class ImagesView(ListView):
	model = Images

	def get(self, *args, **kwargs):
		last_image = self.get_queryset().latest('created_date')
		print "\n\n last image :   ", last_image
		response = HttpResponse('')
		response['image_name'] = last_image.image_name
		print "response image name :    ", response['image_name']

		print "\n\n\n response :   ", response
		return HttpResponse(response)

	def render_to_response(self, context, **reponse_kwargs):
		return self.response

def login(request):
	posted_data = {}
	user=UserDetail(request).getLoginUser()
	if  user:
		if UserDetail(request).is_vendor():
			return redirect("/dashboard")
		else:
			return redirect("/mvpadmin")
	if request.method == "POST":
		posted_data = request.POST
		emailid = request.POST['emailid']
		password = request.POST['password']
		
		form = LoginForm(request.POST, request=request)
		
		if form.is_valid():
			user = Account.objects.get(emailid=emailid)
			# user_id = user.id
			# user_type= user.account_id
			# request.session['user_id'] = user_id
			UserDetail(request).setSession(user)
			if UserDetail(request).is_admin():
				return redirect('/mvpadmin')
			return redirect('/dashboard')
	else:
		form = LoginForm(request=request)
	return render(request, "login.html", {'form': form, 'posted_data': posted_data})

def dashboard(request):	
	user=UserDetail(request).getLoginUser()	
	if not user:
		#messages.add_message(request, messages.INFO, 'Please login firstly !!')
		return redirect("/")
	user_id=user['id']
	products_list = []
	sql='SELECT dp.*, di.* FROM shopify_products AS dp LEFT JOIN (SELECT t1.* FROM images_images t1 WHERE t1.updated_date =(SELECT MAX(t2.updated_date) FROM images_images t2 WHERE t2.product_id = t1.product_id) ) di ON dp.id = di.product_id  where dp.user_id={0} ORDER BY di.product_id'.format(user_id)
	products = Products.objects.raw(sql)
	paginator=Paginator(list(products),6)
	page=request.GET.get("page")
	try:
		products=paginator.page(page)
	except PageNotAnInteger:
		products=paginator.page(1)
	except EmptyPage:
		products=paginator.page(paginator.num_pages)

	login_user = "vendor"
	page_name = "Dashboard"


	if UserDetail(request).is_vendor():
		login_user = "vendor"
	else:
		login_user = "admin"
		page_name = "My Products"

	vendor_name = "My Products"

	return render(request, "dashboard.html", {'products_list': products, 'login_user': login_user, 'page': page, 'vendor_name': vendor_name, 'page_name': page_name})

def logout(request):
	UserDetail(request).clearSession()
	return redirect('/')

def register(request):
	posted_data = {}
	#get the current page url request.build_absolute_uri()
	if request.method == "POST":

		posted_data = request.POST
		form = RegisterForm(request.POST, request=request)
		if form.is_valid():
			first_name = request.POST['first_name']
			last_name = request.POST['last_name']
			emailid = request.POST['emailid']
			password = request.POST['password']

			encrypted_password = handler.encrypt(password)

			if 'vendor' in request.POST:
				account_type=AccountType.objects.get(type="vendor")
			else:
				account_type=AccountType.objects.get(type="user")
				

			detail = Account(first_name=first_name, last_name=last_name, emailid=emailid,  password=encrypted_password,account_id=account_type.id)
			detail.save()
			if account_type.type=="vendor":
				vendor_detail=Vendor(user_id=detail.id,vendor=request.POST['vendor'])
				vendor_detail.save()

				# admin_detail = UserDetail(request).get_admin()
				# admin_email = admin_detail.emailid
				# recipients = [admin_email]
				
				# too = ", ".join(recipients)
				# link = "https://"+request.META['HTTP_HOST']
				# subject, from_email, to = 'Request for Approval of Vendor Account', 'testesfera1@gmail.com', too


				# html_content =render_to_string('account_activation.html', {'link':link}) # ...
				# text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

				# create the email, and attach the HTML version as well.
				# msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
				# msg.attach_alternative(html_content, "text/html")


				#msg.send()

				# fromaddr = "testesfera1@gmail.com"
				# password = "esferasoft"

				# link = "https://"+request.META['HTTP_HOST']

				# admin_detail = UserDetail(request).get_admin()
				# admin_email = admin_detail.emailid

				# msg = MIMEMultipart()
				# msg['From'] = fromaddr

				# recipients = [admin_email]
				# msg['To'] = ", ".join(recipients)

				# msg['Subject'] = "Request for Approval of Label Account"

				# content_html = render_to_string('account_activation.html', {'link':link})

				# test = MIMEText(content_html, 'html')
				# msg.attach(test)

				# server = smtplib.SMTP('smtp.gmail.com', 465)
				# server.starttls()
				# server.login(fromaddr, password)
				# text = msg.as_string()

				# server.sendmail(fromaddr, recipients, text)
				# server.quit()
				messages.add_message(request, messages.SUCCESS, 'Registered Successfully. Please check your mail for approval of your account from admin.')
			return redirect("/")

			#return HttpResponse("Registered Successfully. Please check your mail to activate your account.")
	else:
		form = RegisterForm(request=request)

	return render(request, "register.html", {'form': form, 'posted_data': posted_data})

def add_product(request):
	posted_data = {}
	user=UserDetail(request).getLoginUser()
	if not user:
		#messages.add_message(request, messages.INFO, 'Please login firstly !!')
		return redirect("/")

	user_id=user['id']
	login_user = "vendor"
	page = "add_product"

	if UserDetail(request).is_vendor():
		login_user = "vendor"
	else:
		login_user = "admin"

	if request.method == "POST":
		posted_data = request.POST
		title = request.POST['title']
		description = request.POST['description']
		category = request.POST['category']
		selling_price = float(request.POST['selling_price'])
		compare_price = float(request.POST['compare_price'])

		token = request.POST['token']
		
		if 'is_tax' in request.POST:
			is_tax=request.POST['is_tax']
		else:
			is_tax=0	
		if 'sku' in request.POST:
			sku = request.POST['sku']
		else:
			sku=0	
		barcode = request.POST['barcode']
		user_id=user_id

		form = ProductForm(request.POST, request=request)
		if form.is_valid():
			product_detail = Products(user_id=user_id, title=title, description=description, selling_price=selling_price, compare_price=compare_price, sku=sku, barcode=barcode, category_id=category)
			product_detail.save()
			product_id = product_detail.id

			# images
			Images.objects.filter(token=token).update(product_id=product_id)

			#messages.add_message(request, messages.SUCCESS, 'Products saved successfully')
			if login_user == "vendor":
				return redirect("/dashboard")
			else:
				return redirect('/mvpadmin/products')
	else:
		form = ProductForm(request=request)


	vendor = ''

	categories_list = []

	categories = Categories.objects.filter(user_id=1)
	for category in categories:
		category_id = category.id
		category_name = category.title
		categories_list.append({'category_id': category_id, 'category_name': category_name})
	user_detail = Account.objects.filter(id=user_id)
	# if user_detail:
	# 	vendor = user_detail[0].account_id
	return render(request, "add_product.html", {'categories_list': categories_list, 'login_user': login_user, 'form': form, 'page': page, 'posted_data': posted_data})

def activate_account(request, user_id, activation_key):
	Account.objects.filter(id=user_id, activation_key=activation_key).update(status=1)
	link = "http://"+request.META['HTTP_HOST']

	html = "<h3>Account Activated</h3><p>Your account is activated. Click <a href='{link}'>here</a> to login account.</p>".format(link=link)
	return HttpResponse(html)

def all_products(request):
	user_id = request.session['user_id']

	users = Account.objects.filter(~Q(id=user_id))

	vendors_list = []

	for user in users:

		products_list = []
		vendor_id = user.id
		
		vendor = user.vendor

		products = Products.objects.filter(user_id=vendor_id)
		for product in products:
			title = product.title
			description = product.description
			selling_price = product.selling_price
			wholesale_price = product.wholesale_price
			sku = product.sku
			products_list.append({'title': title, 'description': description, 'selling_price': selling_price, 'wholesale_price': wholesale_price, 'sku': sku})

	vendors_list.append({'vendor': vendor, 'products_list': products_list})

	return render(request, "all_products.html", {'vendors_list': vendors_list})