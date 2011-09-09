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

def diff_list(a,b):	
	return list(set(b) - set(a))

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

class Feed(PyFacebook,PostRequest):
	#create a link, post or status message
	def create_post(self,parameter):
		return self.post_request(comp ="feed" , post =parameter)
	
class Accounts(PyFacebook,PostRequest,DelRequest):
	
	def create_account(self,parameter=None):
		return self.post_request( comp ="accounts/test-users" , post =parameter)
		
	def delete_account(self):
		return self.del_request( comp ="")

			
class Comments(PyFacebook,PostRequest):
	
	def comment(self,message):
		return self.post_request( comp ="comments" , post ={"message":message})
	
	
class Likes(PyFacebook,PostRequest,DelRequest):
	
	def like(self):
		return self.post_request(comp ="likes" , post ="")	
	
	def unlike(self):
		return self.del_request(comp ="likes")	
	
	
class Subscriptions(PyFacebook,PostRequest,DelRequest):	
	
	def create_subscription(self,parameter):
		return self.post_request( comp ="subscriptions" , post =parameter)
		
	def delete_subscription(self,parameter=None): # parameter = {"object","user|permission|page"} If no object is specified all subscriptions are deleted.
		return self.del_request( comp ="subscriptions", param =parameter)
	
class Translations(PyFacebook,PostRequest,DelRequest):	
	
	def create_translation(self,parameter):
		return self.post_request( comp ="translations" , post =parameter)

	def delete_translation(self,parameter):  # parameter = {"native_hashes",An array of native hashes.}
		return self.del_request( comp ="translations" , param =parameter)

class Scores(PyFacebook,PostRequest,DelRequest):	
	
	def read_scores(self,parameter):
		url = "%s%s/scores?access_token=%s" % (GRAPH_URL, self.id ,self.specific_access_token) #app access token
		return self.get_request(url)		

	def delete_scores(self): # parameter = {"achievement","The unique URL to the achievement."}
		return self.del_request( comp ="scores")
		
class Achievements(PyFacebook,PostRequest,DelRequest):	
	
	def create_achievement(self,parameter): #parameter {"achievement":Unique URL to the achievement}
		return self.post_request( comp ="achievements" , post =parameter)		
	
	def read_achievements(self):
		url = "%s%s/achievements?access_token=%s" % (GRAPH_URL, self.id ,self.specific_access_token) #app access token
		return self.get_request(url)		

	def delete_scores(self,parameter): # parameter = {"achievement","The unique URL to the achievement."}
		return self.del_request( comp ="achievements" , param =parameter)		
		

class Banned(PyFacebook,GetRequest,DelRequest):
	
	def get_list(self):
		url = "%s%s/banned?access_token=%s" % (GRAPH_URL, self.id ,self.specific_access_token) #app access token
		return self.get_request(url)		
	
	def is_banned(self,parameter):
		url = "%s%s/banned/%s?access_token=%s" % (GRAPH_URL, self.id ,parameter,self.specific_access_token) #app access token
		return self.get_request(url)	
	
	def ban_user(self,parameter):
		return self.post_request( comp ="banned" , get ={"uid":parameter},post="")	
	
class Rsvp(PyFacebook,PostRequest):	
	
	def maybe(self):
		return self.post_request( comp ="maybe" , post="")	
		
	def attending(self):
		return self.post_request( comp ="attending" ,post="")	
	
	def declined(self):
		return self.post_request( comp ="declined" ,post="")	
	
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
	
	CONN = []
	
	def connection(self,connection=[],**args):
		get = []
		
		if connection in self.CONN or not self.CONN:
			
			for a in args.keys():
				get.append("%s=%s" % (a,args[a]))
			get.append("access_token=%s" % (self.specific_access_token if self.specific_access_token else generic_access_token))
			url = "%s%s/%s?%s" % (GRAPH_URL, self.id ,connection ,"&".join(get))
			return self.get_request(url)
		else:
			return "Unknown connection: %s " % (connection) 
	
	
class Object(PyFacebook,GetRequest):
	
	FIELDS = []
	
	def object(self,**args):	
		
		get = []
			
		if "fields" in args:
			d = diff_list(self.FIELDS,args["fields"])
			if d:
				return "Unknown(s) field(s): %s" % (",".join(d))
			get.append("fields=%s" % (",".join(args["fields"])))
			
		get.append("access_token=%s" % (self.specific_access_token if self.specific_access_token else generic_access_token))
		url = "%s%s/?%s" % (GRAPH_URL,self.id,"&".join(get))
		
		return self.get_request(url)


"""FACEBOOK GRAPH OBJECTS"""	
class Album(Object,Connection,UploadPhoto,Comments,Likes):	
	#http://developers.facebook.com/docs/reference/api/album/
	CONN = ["photos","likes","comments","picture"]	
	FIELDS = ["id","from","name","description","location","link","cover_photo",
			"privacy","count","type","created_time","updated_time"]
	
class Application(Object,Connection,Accounts,Subscriptions,Translations,Scores,Achievements,Banned):	
	#http://developers.facebook.com/docs/reference/api/application/
	CONN = ["accounts","albums","feed","insights","links","picture","posts",
			"reviews","staticresources","statuses","subscriptions","tagged","translations",
			"scores","achievements"]	
	FIELDS = ["id","name","description","category","subcategory","link"]
	
class Checkin(Object,Connection,Comments,Likes):	
	#http://developers.facebook.com/docs/reference/api/checkin/
	CONN = ["comments","likes"]
	FIELDS = ["id","from","tags","place","application","created_time",
			"likes","message","comments","type"] 
	
class Comment(Object,Connection,Likes):	
	#http://developers.facebook.com/docs/reference/api/comment/
	CONN = ["likes"]
	FIELDS = ["id","from","message","created_time","likes","user_likes","type"]
	
class Domain(Object):	
	#http://developers.facebook.com/docs/reference/api/domain/
	FIELDS = ["id","name"]
	
class Event(Object,Connection,Feed,Rsvp):	
	#http://developers.facebook.com/docs/reference/api/event/
	CONN = ["feed","noreply","maybe","invited","attending","declined","picture"]
	FIELDS = ["id","owner","name","description","start_time","end_time","location","venue",
			"privacy","updated_time"]
	
	
class User(Object,Connection,Feed):
	pass
		
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
