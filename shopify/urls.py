from django.conf.urls import url
from views import *
from django.views.generic import TemplateView

urlpatterns = [
	url(r'^$', login, name='login'),
	url(r'^dashboard', dashboard),
	url(r'^logout', logout,name="logout"),
	url(r'^register', register),
	url(r'^products$', all_products),
	url(r'^products/add$', add_product, name="add_product"),
	url(r'^activate_account/(?P<user_id>\d+)/(?P<activation_key>\w+)', activate_account),
	url(r'^accounts', AccountsList.as_view(template_name="shopify/accounts.html")),
	url(r'^categories', CategoryDetailView.as_view()),
	url(r'^testing', TemplateView.as_view(template_name="shopify/accounts.html")),
	#url(r'^vendor', Vendor.as_view()),
	url(r'^latest_image', ImagesView.as_view()),
	url(r'^datatable/data', AccountListJson.as_view(), name='account_list_json'),
	url(r'^people', people),
	url(r'^table/data/$', AccountDataView.as_view(), name='table_data'),
]