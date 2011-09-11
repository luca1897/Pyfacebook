#
# __init__.py
# Copyright (C) orion 2011 <luca.barbara@live.com>
# 
# PyFbGraph is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PyFbGraph is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys 
import urllib2,urllib
import simplejson


GRAPH_URL = "https://graph.facebook.com/"
generic_access_token = ""
client_access_token = None


class PyFacebook(object):
	def __init__(self,id,specific_access_token=None):
		self.set_specific_access_token(specific_access_token)
		self.id=id
	
	def set_specific_access_token(self,access_token):
		self.specific_access_token = access_token 
			
	def get_specific_access_token(self):
		return str(self.specific_access_token)	
	
	def set_id(self,id):
		self.id = id


def init(**args):
	if "access_token" in args and args["access_token"]:
		set_generic_access_token(args["access_token"])
	else:
		if "app_id" in args:
			app_id = args["app_id"]
		else:
			raise FbError("failed: no appID found")
		if "permission" in args:
			permission = args["permission"]
		else:
			permission = ""
			
		if "method" in args:
			method = args["method"]
		else:
			method = qt_method
			
		set_generic_access_token(args={"app_id":app_id,"permission":permission,"method":method})

def set_client_access_token(arg):
	global client_access_token
	client_access_token = arg
	
def get_client_access_token(client_id=None,client_secret=None):
	global client_access_token
	if not client_access_token:
		url = "%soauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" % (GRAPH_URL,client_id,client_secret)
		request = urllib2.Request(url)
		set_client_access_token(Request().request(request).split("=")[1])
	return client_access_token

	
def set_generic_access_token(access_token="",args=None):
	global generic_access_token
	if access_token:
		generic_access_token = access_token
	else:
		print args["method"]
		generic_access_token = args["method"](args["app_id"],args["permission"])
			
def get_generic_access_token():
	return str(generic_access_token)	
	
	
"""REQUEST"""	
class Request(object):
				
	def request(self,request,post=None):
		if post:
			post = urllib.urlencode(post)

		res = urllib2.urlopen(request,post).read()
		try:
			data = simplejson.loads(res)
			if type(data) == dict:
				if data.get("error"):
					raise FbError(data["error"]["message"]) 	
				else:
					return data
			else:
				return res
		except ValueError:
			return res


class PostFileRequest(Request):
	
	def post_file_request(self,**args):
		url = "%s%s/photos/?access_token=%s" % (GRAPH_URL,self.id,self.specific_access_token if self.specific_access_token else generic_access_token)
		
		request = urllib2.Request(url)
		request.add_header('Content-type', 'multipart/form-data; boundary=%s'% ('PyFbGraph'))
		request.add_header('Content-length', len(args["body"]))
		request.add_data(args["body"])		
		return self.request(request)


class PostRequest(Request):	
	
	def post_request(self,**args):
		
		get = []
		if "get" in args:
			for i in args["get"]:
				get.append("%s=%s" % (i,args["get"][i]))
				
		get.append("access_token=%s" % (self.specific_access_token if self.specific_access_token else generic_access_token)) 		
			
		
		url = "%s%s/%s?%s" % (GRAPH_URL, self.id, args["comp"], "&".join(get))
		request = urllib2.Request(url)
		return self.request(request,args["post"])
	
	
class GetRequest(Request):	
	
	def get_request(self,url):
		request = urllib2.Request(url)
		return self.request(request)	


class DelRequest(Request):	
	
	def del_request(self,**args):
		
		get = []
		if "param" in args:
			for p in args["param"]:
				get.append("%s=%s" % (p,args["param"][p]))		
		
		get.append("access_token=%s" % (self.specific_access_token if self.specific_access_token else generic_access_token)) 
		
		url = "%s%s/%s?%s" % (GRAPH_URL, self.id, args["comp"],"&".join(get))
		request = urllib2.Request(url)
		request.get_method = lambda: 'DELETE'
		return self.request(request)

""" METHOD """	
	
class UploadFiles(PyFacebook,PostFileRequest):
	
	def upload_files(self,args):
		import mimetypes
		
		ret = []
		
		for a in args:
			body = []
			mimetype = mimetypes.guess_type(a["filename"])[0] or 'application/octet-stream' 
			
			filehandle = open(a["filename"])
			
			#File description
			for p in a["param"]:
				body.append('--PyFbGraph')
				body.append('Content-Disposition: form-data; name="%s"' % (p))
				body.append('')
				body.append(a["param"][p])	
							
			#File Content
			body.append('--PyFbGraph')
			body.append('Content-Disposition: file; name="source"; filename="%s"' % (a["filename"]))
			body.append('Content-Type: %s' % mimetype)
			body.append('')
			body.append(filehandle.read())
			body.append('')
			filehandle.close()
			
			body.append('--PyFbGraph--')
			body.append('')	
			
			ret.append(self.post_file_request(body='\r\n'.join(body)))
		
		return ret		
	

	
class Connection(PyFacebook,GetRequest):
	
	def connection(self,connection=[],**args):
		get = []	
			
		for a in args.keys():
			get.append("%s=%s" % (a,args[a]))
		get.append("access_token=%s" % (self.specific_access_token if self.specific_access_token else generic_access_token))
		url = "%s%s/%s?%s" % (GRAPH_URL, self.id ,connection ,"&".join(get))
		return self.get_request(url)
	
	
class Object(PyFacebook,GetRequest):
	
	def object(self,**args):	
			
		if "fields" in args:
			get.append("fields=%s" % (",".join(args["fields"])))
			
		get.append("access_token=%s" % (self.specific_access_token if self.specific_access_token else generic_access_token))
		url = "%s%s/?%s" % (GRAPH_URL,self.id,"&".join(get))
		
		return self.get_request(url)

		
""" ACCESS TOKEN """		
class common_method():
	access_token = ""

	REDIRECT_URL = "&redirect_uri=https://www.facebook.com/connect/login_success.html"

	def __init__(self,app_id,permission):
		if permission:
			scope = "&scope=" + ",".join(permission)
		self.OAUTH_URL = "https://www.facebook.com/dialog/oauth?client_id=" + app_id + self.REDIRECT_URL + scope + "&response_type=token"
		self.create_browser()
		
	def load_finished(self):
		url = self.get_url()
		if url.find("https://www.facebook.com/connect/login_success.html#access_token=")>=0:
			self.access_token = url[url.find("=")+1:url.find("&expires_in")]
			self.destroy()				
		
	def __str__(self):
		return self.access_token	
		
class webkitgtk_method(common_method):		
	def create_browser(self):
		try:
			import gtk 
			import webkit 
		except ImportError: 
			raise self.raise_error("You need pywebkitgtk\nDownload: http://code.google.com/p/pywebkitgtk/")
				
		self.web = webkit.WebView() 
		
		
		win = gtk.Window(gtk.WINDOW_TOPLEVEL) 
		win.add(self.web) 
		win.show_all() 
		
		self.web.open(self.OAUTH_URL) 
		self.web.connect("load-finished", self.load_finished)
		self.gtk.main()			
		
	def get_url(self):
		return self.web.get_main_frame().get_uri()
	
	def destroy(self):
		self.web.destroy()
		self.gtk.main_quit()		
				

class qt_method(common_method):
	def create_browser(self):
		try: 
			from PySide.QtCore import QUrl
			from PySide.QtGui import QApplication
			from PySide.QtWebKit import QWebView 
		except ImportError: 
			raise self.raise_error("You need python-pyside\nDownload: http://developer.qt.nokia.com/wiki/PySide_Binaries_Linux")

		
		self.app = QApplication(sys.argv)
		self.web = QWebView()
		self.web.load(QUrl(self.OAUTH_URL))
		self.web.loadFinished[bool].connect(self.load_finished)
		self.web.show()
		self.app.exec_()
		
	
	def get_url(self):	
		return self.web.url().toString()
	
	def destroy(self):
		self.web.close()
		self.app.exit()
		
"""EXCEPTION"""		
class FbError(Exception):
	
	def raise_error(self, message):
		Exception.__init__(self, message)	
