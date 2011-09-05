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
access_token = ""

def diff_list(a,b):	
	return list(set(b) - set(a))


def set_access_token(arg):
	global access_token
	access_token = arg
	
	
def get_access_token():
	if access_token=="":
		raise FbError("Invalid access token")
	return str(access_token)


def init(**args):
	if "access_token" in args:
		set_access_token(args["access_token"])
	else:
		if "id_app" in args:
			id_app = args["id_app"]
		else:
			raise FbError("failed: no appID found")
		if "permission" in args:
			permission = args["permission"]
		else:
			permission = ""
		set_access_token(AccessToken(id_app,permission))
	
		
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


class PutFile(Request):
	
	def putFile(self,url,body):
		request = urllib2.Request(url)
		request.add_header('Content-type', 'multipart/form-data; boundary=%s'% ('PyFbGraph'))
		request.add_header('Content-length', len(body))
		request.add_data(body)		
		return self.request(request)


class PutObject(Request):	
	
	def put_object(self,**args):
		url = "%s%s/%s?access_token=%s" % (GRAPH_URL, args["id"], args["comp"], get_access_token())
		request = urllib2.Request(url)
		return self.request(request,args["post"])
	
	
class GetObject(Request):	
	
	def get_object(self,url):
		print url
		request = urllib2.Request(url)
		return self.request(request)	


class DelObject(Request):	
	
	def del_object(self,**args):
		url = "%s%s/%s?access_token=%s" % (GRAPH_URL, args["id"], args["comp"], get_access_token())
		request = urllib2.Request(url)
		request.get_method = lambda: 'DELETE'
		return self.request(request)


class UploadPhoto(PutFile):
	
	def upload_photo(self,id,photos):
		import mimetypes
		url = GRAPH_URL + id + "/photos?access_token=" + get_access_token()
		
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

			ret.append(self.putFile(url,'\r\n'.join(body)))
		
		return ret


class Comment(PutObject):
	
	def comment(self,id,message):
		return self.put_object(id = id, comp ="comments" , post ={"message":message})
	
	
class Likes(PutObject,DelObject):
	
	def like(self,id):
		return self.put_object(id = id, comp ="likes" , post ="")	
	
	
	def unlike(self,id):
		return self.del_object(id = id, comp ="likes")	
	
	
class Connections(GetObject):
	
	CONN = []
	
	def connection(self,id,connection,access_token="",**args):
		get = []
		if access_token == "":
			access_token = get_access_token()
		
		if connection in self.CONN:
			
			for a in args.keys():
				get.append("%s=%s" % (a,args[a]))
			get.append("access_token=%s" % (access_token))
			url = "%s%s/%s?%s" % (GRAPH_URL, id ,connection ,"&".join(get))
			return self.get_object(url)
		else:
			return "Unknown connection: %s " % (connection) 
	
	
	def connections(self,args):
		data = []
		for a in args:
			if "access_token" not in a:
				access_token=""
			data.append(self.connection(a["id"],a["connection"],access_token))
		return data
	
	
class Object(GetObject):
	
	FIELDS = []
	
	def object(self,id,access_token="",**args):	
		
		get = []
		if access_token == "":
			access_token = get_access_token()
			
		if "fields" in args:
			d = diff_list(self.FIELDS,args["fields"])
			if d:
				return "Unknown(s) field(s): %s" % (",".join(d))
			get.append("fields=%s" % (",".join(args["fields"])))
			
		get.append("access_token=" + access_token)
		url = "%s%s/?%s" % (GRAPH_URL,id,"&".join(get))
		
		return self.get_object(url)

"""FACEBOOK GRAPH OBJECTS"""	
class Album(UploadPhoto,Object,Connections,Comment,Likes):	
	
	CONN = ["photos","likes","comments","picture"]	
	FIELDS = ["id","from","name","description","location","link","cover_photo",
			"privacy","count","type","created_time","updated_time"]
	
class Application(Object,Connections):	
	
	CONN = ["accounts","albums","feed","insights","links","picture","posts",
			"reviews","staticresources","statuses","subscriptions","tagged","translations",
			"scores","achievements"]	
	FIELDS = ["id","name","description","category","subcategory","link"]
	
		
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
