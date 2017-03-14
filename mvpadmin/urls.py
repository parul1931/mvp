from django.conf.urls import url
from . import views
from shopify.views import add_product, dashboard


urlpatterns=[
 url(r'^$',views.index,name="mvpadmin"),
 url(r'^labels$',views.vendors_list, name="vendors"),
 url(r'^labels/products',views.vendors, name="vendors"),
 url(r'^products$', dashboard),
 url(r'^products/add$', add_product, name="add_product"),
 url(r'^user_status', views.user_status),
]