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

	
def init(**args):
	if "access_token" in args:
		set_generic_access_token(args["access_token"])
	else:
		if "id_app" in args:
			id_app = args["id_app"]
		else:
			raise FbError("failed: no appID found")
		if "permission" in args:
			permission = args["permission"]
		else:
			permission = ""
		set_generic_access_token(AccessToken(id_app,permission))
	
def set_generic_access_token(access_token):
	global generic_access_token
	generic_access_token = access_token
			
def get_generic_access_token():
	return str(generic_access_token)	
	
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
			
class FbError(Exception):
	
	def raise_error(self, message):
		Exception.__init__(self, message)
	
	
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

	
class UploadPhoto(PyFacebook,PostFileRequest):
	
	def upload_photo(self,photos):
		import mimetypes
		
		ret = []
		for f in photos:
			body = []
			mimetype = mimetypes.guess_type(f["filename"])[0] or 'application/octet-stream'
			
			filehandle = open(f["filename"])
		
			#Photo description
			body.append('--PyFbGraph')
			body.append('Content-Disposition: form-data; name="message"')
			body.append('')
			body.append(f["message"])
			#Photo content
			body.append('--PyFbGraph')
			body.append('Content-Disposition: file; name="source"; filename="%s"' % (f["filename"]))
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

		
class AccessToken(FbError):

	def __init__(self,idapp,permission=None): 
		self.access_token = ""
		
		if permission:
			scope = "&scope=" + ",".join(permission)
		self.REDIRECT_URL = "&redirect_uri=https://www.facebook.com/connect/login_success.html"
		#OAUTH URL
		self.OAUTH_URL = "https://www.facebook.com/dialog/oauth?client_id=" + idapp + self.REDIRECT_URL + scope + "&response_type=token"
		
		self.get_access_token()
		if self.access_token=="":
			raise self.raise_error("Access Token is not valid") 	
			
			
	def get_access_token(self):
		try: 
			from PySide.QtCore import QUrl
			from PySide.QtGui import QApplication
			from PySide.QtWebKit import QWebView 
		except ImportError: 
			raise self.raise_error("You need python-pyside\nDownload: http://developer.qt.nokia.com/wiki/PySide_Binaries_Linux")

		
		self.app = QApplication(sys.argv)
		self.web = QWebView()
		self.web.load(QUrl(self.OAUTH_URL))
		self.web.loadFinished[bool].connect(self.loadfinished)
		self.web.show()
		self.app.exec_()


	def loadfinished(self):
		url = self.web.url().toString()
		if url.find("https://www.facebook.com/connect/login_success.html#access_token=")>=0:
			self.access_token = url[url.find("=")+1:url.find("&expires_in")]
			self.web.close()
			self.app.exit()
			
			
	def __str__(self):
		return self.access_token	
