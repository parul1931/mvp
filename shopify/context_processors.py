def user_detail(request):
	user_name = ''
	account_type={"admin":False,"user":False,"vendor":False}
	admin = False
	if 'user' in request.session:
		user_name=	request.session['user']['user_name']
		print "\n\n\n user name :    ", user_name
		account_type = request.session['user']['account_type']
		print "\n\n account type :   ", account_type
	return {'user_name': user_name,'account_type':account_type}
