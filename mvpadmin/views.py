from django.shortcuts import render,redirect
from shopify.utils.userdetails import UserDetail
from django.http import HttpResponse
from shopify.models import Account, Products, Vendor
from django.db.models import Q
from django.template.loader import render_to_string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def index(request):
	if UserDetail(request).is_vendor():
		return redirect("/dashboard")

	total_vendors = Account.objects.filter(account_id=3).count()
	return render(request,"index.html", {'total_vendors': total_vendors, 'page': 'dashboard'})

def vendors(request):

	user=UserDetail(request).getLoginUser()	
	if not user:
		#messages.add_message(request, messages.INFO, 'Please login firstly !!')
		return redirect("/")
	else:
		account_type = user['account_type']['admin']

		if account_type == False:
			return render(request, "not_allowed.html", {})

	user_id = request.GET['user_id']
	
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
	page = "dashboard"

	if UserDetail(request).is_vendor():
		login_user = "vendor"
	else:
		login_user = "admin"
		page = "products"

	vendor_detail = Vendor.objects.get(user_id=user_id)
	vendor_name = vendor_detail.vendor

	page_name = "Vendor Products"

	return render(request, "dashboard.html", {'products_list': products, 'login_user': login_user, 'page': page, 'vendor_name': vendor_name, 'page_name': page_name, 'user_id': user_id})

def vendors_list(request):

	user=UserDetail(request).getLoginUser()	
	if not user:
		#messages.add_message(request, messages.INFO, 'Please login firstly !!')
		return redirect("/")
	else:
		account_type = user['account_type']['admin']

		if account_type == False:
			return render(request, "not_allowed.html", {})
	users = Account.objects.filter(account_id=3)

	users_list = []

	for user in users:
		fname = user.first_name
		lname = user.last_name
		user_name = fname + " " + lname
		user_name = user_name.title()
		status = user.status
		user_id = user.id
		vendor_detail = Vendor.objects.get(user_id=user_id)
		vendor_name = vendor_detail.vendor
		users_list.append({'user_name': vendor_name, 'status': status, 'user_id': user_id})

	paginator=Paginator(list(users_list),10)
	page=request.GET.get("page")
	try:
		users_list=paginator.page(page)
	except PageNotAnInteger:
		users_list=paginator.page(1)
	except EmptyPage:
		users_list=paginator.page(paginator.num_pages)

	return render(request, "vendors_list.html", {'page': 'vendors_list', 'users_list': users_list})

def user_status(request):
	user_id = request.POST['user_id']
	status = request.POST['status']

	user_detail = Account.objects.get(id=user_id)
	emailid = user_detail.emailid
	existing_status = user_detail.status

	if int(existing_status) == int(status):
		response = {'already_updated': 'Vendor Account is already updated.'}
		return HttpResponse(json.dumps(response))

	try:
		Account.objects.filter(id=user_id).update(status=status)

		fromaddr = "testesfera1@gmail.com"
		password = "esferasoft"

		msg = MIMEMultipart()
		msg['From'] = fromaddr

		recipients = [emailid]
		msg['To'] = ", ".join(recipients)

		if int(status) == 1:
			print "\n\n enabled"

			msg['Subject'] = "Enabled Vendor Account"

			link = "http://"+request.META['HTTP_HOST']

			content = '<html><head></head><body><h3><b>Your vendor Account is enabled by admin.</b></h3><p>Please click <a href="{link}">here</a> to approve the vendor account.<br></p></body></html>'.format(link=link)
		else:
			print "\n\n disabled"

			msg['Subject'] = "Disabled Vendor Account"

			content = '<html><head></head><body><h3><b>Your vendor Account is disabled by admin. You cannot use your account further.</b></h3></body></html>'

		test = MIMEText(content, 'html')
		msg.attach(test)

		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(fromaddr, password)
		text = msg.as_string()

		server.sendmail(fromaddr, recipients, text)
		server.quit()
	except:
		response = {'error': 'Sorry, Error while Updating.'}
		return HttpResponse(json.dumps(response))
	response = {'success': 'Successfully Updated.'}
	return HttpResponse(json.dumps(response))