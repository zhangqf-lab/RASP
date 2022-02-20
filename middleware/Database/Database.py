

#from types import MethodType
#from django.http import CompatCookie, HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse


class RequestCookies(MiddlewareMixin):
	"""
	Allows setting and deleting of cookies from requests in exactly the same
	way as responses.
	
	>>> request.set_cookie('name', 'value')
	
	The set_cookie and delete_cookie are exactly the same as the ones built
	into the Django HttpResponse class. 
	http://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse.set_cookie
	"""
	def process_request(self, request):
		userid = request.COOKIES.get('userid', None)
		if userid is not None:
			print("User ID=======>", userid)
		else:
			print("=======>No User ID<=======")
		#request._resp_cookies = CompatCookie()
		#request.set_cookie = MethodType(_set_cookie, request, HttpRequest)
		#request.delete_cookie = MethodType(_delete_cookie, request, HttpRequest)
	
	def process_response(self, request, response):
		if isinstance(response, HttpResponse):
			#response.set_cookie("userid", value='12345', max_age=36000000, expires=None, path='/', domain=None, secure=False, httponly=False, samesite=None)
			pass
		return response




#并且在settings.py的MIDDLEWARE中加入我们的中间件：
#'middleware.thisapp.thisapp_mw.MyMiddle'

