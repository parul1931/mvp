from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from shopify.models import Account, Products, Categories, AccountType, Vendor
from serializers import AccountSerializer, ProductsSerializer, CategoriesSerializer, AccountTypeSerializer, VendorSerializer
from images.models import Images
from rest_framework import generics

from rest_framework.decorators import api_view

from rest_framework.views import APIView

from django.http import JsonResponse


#####################################
# 1.) Vendor List
class VendorList(APIView):

	def get(self, request):
		vendors = Vendor.objects.all()
		serializer = VendorSerializer(vendors, many=True)
		vendor = {'Vendors': serializer.data}
		return JsonResponse(vendor, safe=False)


class ProductsList(APIView):

	def get(self, request, user_id):
		products = Products.objects.filter(user_id=user_id)
		serializer = ProductsSerializer(products, many=True, context={'request': request})
		product = {'Products': serializer.data}
		return JsonResponse(product, safe=False)


class AllProductsList(APIView):

	def get(self, request):
		products = Products.objects.all()
		serializer = ProductsSerializer(products, many=True, context={'request': request})
		product = {'Products': serializer.data}
		return Response(product)

	

########################
## vendor products api
class VendorDetail(APIView):

	def get(self, request):
		vendor = Vendor.objects.all()
		print "\n\n vendor :   ", vendor
		serializer = VendorSerializer(vendor, many=True)
		print "\n\n\n!!!!!!!!"
		print "serializer data :   ", serializer.data

		all_vendors = []

		for user in serializer.data:

			vendors = {}
			
			vendors['vendor'] = user['vendor']

			all_products = []

			products = Products.objects.filter(user_id=user['user'])

			for d in products:

				products_list = {}
				product_id = d.id
				products_list['product_id'] = product_id

				title = d.title
				products_list['title'] = title

				description = d.description
				products_list['description'] = description

				selling_price = d.selling_price
				products_list['selling_price'] = selling_price

				compare_price = d.compare_price
				products_list['compare_price'] = compare_price

				is_tax = d.is_tax
				products_list['is_tax'] = is_tax

				sku = d.sku
				products_list['sku'] = sku

				barcode = d.barcode
				products_list['barcode'] = barcode

				category = d.category
				
				products_list['category_name'] = category.title

				url="/images/view/"

				images_list = []

				images = Images.objects.filter(product_id=product_id)
				for image in images:
					image_path = ''
					print "\n\n image :   ", image.image_name
					image_id = image.id
					token = image.token
					if token:
						image_path = "http://"+request.META['HTTP_HOST'] + url + str(token) + "/" + str(image_id)
						print "\n\n image path :   ", image_path
						images_list.append(image_path)

				products_list['images'] = images_list
				all_products.append(products_list)
			vendors['products'] = all_products

			all_vendors.append(vendors)

		vendors_list = {'vendors': all_vendors}

		return Response(vendors_list)


####################################
# all products api
@api_view(['GET'])
def products_detail(request):
	products = Products.objects.all()
	serializer = ProductsSerializer(products, many=True)
	data = serializer.data

	all_products = []

	for d in data:
		products_list = {}
		product_id = d['id']
		products_list['product_id'] = product_id

		title = d['title']
		products_list['title'] = title

		description = d['description']
		products_list['description'] = description

		selling_price = d['selling_price']
		products_list['selling_price'] = selling_price

		compare_price = d['compare_price']
		products_list['compare_price'] = compare_price

		is_tax = d['is_tax']
		products_list['is_tax'] = is_tax

		sku = d['sku']
		products_list['sku'] = sku

		user = d['user']

		vendor_detail = Vendor.objects.get(user_id=user)
		vendor = vendor_detail.vendor
		products_list['vendor'] = vendor

		barcode = d['barcode']
		products_list['barcode'] = barcode

		category = Categories.objects.get(id=d['category'])
		category_name = category.title
		products_list['category_name'] = category_name

		url="/images/view/"

		images_list = []

		images = Images.objects.filter(product_id=product_id)
		for image in images:
			image_path = ''
			print "\n\n image :   ", image.image_name
			image_id = image.id
			token = image.token
			if token:
				image_path = "http://"+request.META['HTTP_HOST'] + url + str(token) + "/" + str(image_id)
				print "\n\n image path :   ", image_path
				images_list.append(image_path)

		products_list['images'] = images_list
		all_products.append(products_list)
	products = {'Products': all_products}

	return Response(products)



############# api functions
@api_view(['GET', 'POST'])
def accounts_detail(request):
	if request.method == "GET":
		records = Account.objects.all()
		serializer = AccountSerializer(records, many=True)
		return Response(serializer.data)

	elif request.method == "POST":
		serializer = AccountSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def categories_detail(request):
	categories = Categories.objects.all()
	serializer = CategoriesSerializer(categories, many=True, context={'request': request})
	return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def account_types(request):
	types = AccountType.objects.all()
	serializer = AccountTypeSerializer(types, many=True)
	return Response(serializer.data)


########### api classes
class AccountList(APIView):
	def get(self, request):
		accounts = Account.objects.all()
		serializer = AccountSerializer(accounts, many=True)
		return Response(serializer.data)

	def post(self, request):
		serializer = AccountSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class AccountDetail(APIView):

	def get(self, request, id):
		account = Account.objects.get(id=id)
		serializer = AccountSerializer(account)
		return Response(serializer.data)



################# api generics
class AccountGenericList(generics.ListCreateAPIView):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer


class AccountUpdateGenericList(generics.RetrieveUpdateDestroyAPIView):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer


class AccountListView(generics.ListAPIView):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer


class AccountRetrieveView(generics.RetrieveAPIView):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer