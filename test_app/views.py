from django.shortcuts import render
from django.views.generic.edit import FormView
from shopify.forms import RegisterForm, LoginForm
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse


class RegisterView(FormView):
	template_name = 'test_register.html'
	form_class = RegisterForm
	success_url = reverse_lazy('login')

	def get_form_kwargs(self):
		kwargs = super(RegisterView, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def form_valid(self, form):
		print "\n\n\n register successfully."
		# return HttpResponse("done")
		return super(RegisterView, self).form_valid(form)

	def get_context_data(self, **kwargs):
		data = super(RegisterView, self).get_context_data(**kwargs)
		data['posted_data'] = self.request.POST
		return data


class LoginView(FormView):
	template_name = 'test_login.html'
	form_class = LoginForm

	def get_form_kwargs(self):
		kwargs = super(LoginView, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def form_valid(self, form):
		print "\n\n login successfully."
		return HttpResponse("Login successfully.")

	def get_context_data(self, **kwargs):
		data = super(LoginView, self).get_context_data(**kwargs)
		data['posted_data'] = self.request.POST
		return data
