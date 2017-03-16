from rest_framework import serializers
from shopify.models import Account, Categories, Products, AccountType, Vendor
from passlib.hash import django_pbkdf2_sha256 as handler
from images.models import Images
from django.conf import settings


class AccountSerializer(serializers.ModelSerializer):

	class Meta:
		model = Account
		fields = ('id', 'first_name', 'last_name', 'emailid')
		extra_kwargs = {'password': {'write_only': True}, 'activation_key': {'write_only': True}}
		#fields = '__all__'
		#exclude = ('status', 'activation_key', 'password')

		def create(self, validated_data):
			record = Account(first_name=validated_data['first_name'], last_name=validated_data['last_name'], emailid=validated_data['emailid'])
			encrypted_password = handler.encrypt(validated_data['password'])
			record.set_password(encrypted_password)
			record.save()
			return record


class AccountTypeSerializer(serializers.ModelSerializer):
	accounts = AccountSerializer(source='account_set', many=True)
	class Meta:
		model = AccountType
		fields = '__all__'


class ProductsSerializer(serializers.ModelSerializer):

	user_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(),source='user.id')

	images = serializers.SerializerMethodField('image_serializer')

	label = serializers.SerializerMethodField('vendor_serializer')

	def image_serializer(self, obj):
		images_list = []

		url="/images/view/"

		image_detail = Images.objects.filter(product_id=obj.id)
		for image in image_detail:
			image_name = image.image_name
			image_id = image.id
			token = image.token
			if token:
				image_path = "https://"+self.context['request'].META['HTTP_HOST'] + url + str(token) + "/" + str(image_id)
				images_list.append(image_path)

		if not images_list:
			default_image = "https://"+self.context['request'].META['HTTP_HOST'] + "/media/default_image.gif"
			images_list.append(default_image)
		return images_list

	def vendor_serializer(self, obj):
		vendor_detail = Vendor.objects.get(user_id=obj.user_id)
		return vendor_detail.vendor


	class Meta:
		model = Products
		fields = '__all__'
		

class CategoriesSerializer(serializers.ModelSerializer):
	products = ProductsSerializer(source='products_set', many=True)

	class Meta:
		model = Categories
		fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Vendor
		fields = ('vendor', 'user_id')
