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

class PyFacebook(object):
	def __init__(self,id=None,specific_access_token=None):
		self.set_specific_access_token(specific_access_token)
		self.id=id

	def Request(self,get={},post=None,delete=False,**args):

		if post:
			post = urllib.urlencode(post)
			
		get["access_token"] = self.specific_access_token if self.specific_access_token else get_generic_access_token()
		
		get = urllib.urlencode(get)
			
		url = "%s%s/%s?%s" % (GRAPH_URL, self.id, args["method"], get)
		print url
		req = urllib2.Request(url)
		
		if delete:
			req.get_method = lambda: 'DELETE'	
		elif "body" in args:		
			req.add_header('Content-type', 'multipart/form-data; boundary=%s'% ('PyFbGraph'))
			req.add_header('Content-length', len(args["body"]))
			req.add_data(args["body"])
			
					
		try:
			res = urllib2.urlopen(req, post).read()
		except urllib2.HTTPError, e:
			res = e.read()	 
		
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
		set_client_access_token(urllib2.urlopen(url).read().split("=")[1])
	return client_access_token

	
def set_generic_access_token(access_token="",args=None):
	global generic_access_token
	if access_token:
		generic_access_token = access_token
	else:
		generic_access_token = args["method"](args["app_id"],args["permission"])
			
def get_generic_access_token():
	return str(generic_access_token)	
	


"""METHOD"""	

class Feed():
	"""create a link, post or status message"""
	def create_post(self,parameter):
		return self.Request(method="feed" , post =parameter)
			
class Comments():
	
	def comment(self,message):
		"""comment on album/Status ecc"""
		return self.Request(method ="comments" , post ={"message":message})
	
	def del_comment(self):
		"""delete a comment"""
		return self.Request(delete=True,method ="")	
	
	
class Likes():
	
	def like(self):
		"""like an album/comment/post"""
		return self.Request(method ="likes" , post ="")	
	
	def unlike(self):
		"""unlike an album/comment/post"""
		return self.Request(delete=True,method ="likes")	
		

class Man_friendlist():	
	
	def create_friendlist(self,name):
		"""create a FriendList"""
		return self.Request(method ="friendlists" , post={"name":name})
	
	def delete_friendlist(self):
		"""delete a FriendList"""
		return self.Request(delete=True,method ="")		
	
	def add_member(self,id):
		"""add a user to a FriendList"""
		return self.Request(method ="members/%s" % id , post="")
	
	def remove_member(self,id):
		"""remove a user from a FriendList"""
		return self.Request(delete=True,method ="members/%s" % id)	
			
	
class Man_event():	
	
	def create_event(self,**args):
		"""create an event"""
		return self.Request(method ="events" , post=args)
	

class Man_note():
	
	def create_note(self,subject,message):
		"""create a note"""
		return self.Request(method ="notes" , post={"subject":subject,"message":message})

				
class Man_album():		
	
	def create_album(self,**args):		
		"""create an album for a user"""
		return self.Request( method ="albums", post =args)
			
	
class UploadFiles():
	
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
			
			ret.append(self.Request(method="photos",body='\r\n'.join(body)))
		
		return ret	
	
	
class Connection():
	
	CONN = []
	
	def connection(self,connection=[],**args):
		
		if connection in self.CONN or not self.CONN:
			return self.Request(method=connection,get=args)
		else:
			return "Unknown connection: %s " % (connection) 
	
	
class Object():
	
	FIELDS = []
	
	def object(self,**args):	
		
		get = []
			
		if "fields" in args:
			d = diff_list(self.FIELDS,args["fields"])
			if d:
				return "Unknown(s) field(s): %s" % (",".join(d))
			get.append({"fields":",".join(args["fields"])})
					
		return self.Request(method="",get=args)


"""FACEBOOK GRAPH OBJECTS"""	
class Album(PyFacebook,Object,Connection,UploadFiles,Comments,Likes):	
	#http://developers.facebook.com/docs/reference/api/album/
	CONN = ["photos","likes","comments","picture"]	
	FIELDS = ["id","from","name","description","location","link","cover_photo",
			"privacy","count","type","created_time","updated_time"]
	
	
class Application(PyFacebook,Object,Connection):	
	#http://developers.facebook.com/docs/reference/api/application/
	CONN = ["accounts","albums","feed","insights","links","picture","posts",
			"reviews","staticresources","statuses","subscriptions","tagged","translations",
			"scores","achievements"]	
	FIELDS = ["id","name","description","category","subcategory","link"]
	
	def create_account(self,**args):
		"""create a test account for an application"""
		
		return self.Request( method ="accounts/test-users" , post =args)
		
	def delete_account(self):
		"""delete a test account"""
		return self.Request(delete=True, method ="")		
	
	def create_subscription(self,**args):
		"""set up a subscription"""
		return self.Request( method ="subscriptions" , post =args)
		
	def delete_subscription(self,object=None): # object = {"object","user|permission|page"} If no object is specified all subscriptions are deleted.
		"""delete subscriptions"""
		return self.Request(delete=True,method ="subscriptions", get ={"object":object})
		
	
	def create_translation(self,native_strings):
		"""upload application strings for translation"""
		return self.Request( method ="translations" , post ={"native_strings":native_strings})

	def delete_translation(self,native_hashes):
		"""delete a translation string"""
		return self.Request(delete=True,method ="translations" , param ={"native_hashes":native_hashes})
	
	
	def read_scores(self,parameter):
		"""read the scores for the user and their friends for your app"""
		return self.Request(method="scores")		

	def delete_scores(self): # parameter = {"achievement","The unique URL to the achievement."}
		"""delete all the scores for an app"""
		return self.Request(delete=True,method ="scores")
		
	
	def create_achievement(self,**args): #parameter {"achievement":Unique URL to the achievement}
		"""register an achievement"""
		return self.Request( method ="achievements" , post =args)		
	
	def read_achievements(self):
		"""get all achievements"""
		return self.Request(method="achievements")		

	def delete_achievements(self,achievement): # parameter = {"achievement","The unique URL to the achievement."}
		"""un-register an achievement"""
		return self.Request(delete=True,method ="achievements" , get ={"achievement":achievement})		
		
	
	def get_banned_list(self):
		"""retrieve a list of banned users"""
		return self.Request(method="banned")		
	
	def is_banned(self,u_id):
		"""test if a given user is banned"""
		return self.Request(method="banned%s" % u_id)	

	def ban_user(self,u_id):
		"""ban a user"""
		return self.Request( method ="banned" , get ={"uid":u_id},post="")
	
	def unban_user(self,u_id):
		"""unban a user"""
		return self.Request(delete=True,method ="banned" , get ={"uid":u_id},post="")	
	

	
class Checkin(PyFacebook,Object,Connection,Comments,Likes):	
	#http://developers.facebook.com/docs/reference/api/checkin/
	CONN = ["comments","likes"]
	FIELDS = ["id","from","tags","place","application","created_time",
			"likes","message","comments","type"] 
	
class Comment(PyFacebook,Object,Connection,Likes):	
	#http://developers.facebook.com/docs/reference/api/comment/
	CONN = ["likes"]
	FIELDS = ["id","from","message","created_time","likes","user_likes","type"]
	
class Domain(PyFacebook,Object):	
	#http://developers.facebook.com/docs/reference/api/domain/
	FIELDS = ["id","name"]
	
class Event(PyFacebook,Object,Connection,Feed):	
	#http://developers.facebook.com/docs/reference/api/event/
	CONN = ["feed","noreply","maybe","invited","attending","declined","picture"]
	FIELDS = ["id","owner","name","description","start_time","end_time","location","venue",
			"privacy","updated_time"]
	
	def maybe(self):
		"""RSVP the user as a 'maybe' for an Event"""
		return self.Request( method ="maybe" , post="")	
		
	def attending(self):
		"""RSVP the user as 'attending' an Event"""
		return self.Request( method ="attending" ,post="")	
	
	def declined(self):
		"""RSVP the user as 'declined' for an Event"""
		return self.Request( method ="declined" ,post="")		
	
	
	
class Friendlist(PyFacebook,Object,Connection,Man_friendlist):	
	#http://developers.facebook.com/docs/reference/api/FriendList/
	CONN = ["members"]
	FIELDS = ["id","name","type"]
	
class Group(PyFacebook,Object,Connection,Feed):	
	#http://developers.facebook.com/docs/reference/api/group/
	CONN = ["feed","members","picture","docs"]
	FIELDS = ["id","version","icon","owner","name","description","link","privacy",
			"updated_time"]	
	
class Insights(PyFacebook,Object):	
	#http://developers.facebook.com/docs/reference/api/insights/
	FIELDS = ["id","name","period","values","description"]
	
class Link(PyFacebook,Object,Connection,Comments):	
	#http://developers.facebook.com/docs/reference/api/link/
	CONN = ["comments","likes"]
	FIELDS = ["id","from","link","name","comments","description","icon",
			"picture","message","created_time","type"]
	
class Message(PyFacebook,Object):
	#http://developers.facebook.com/docs/reference/api/message/
	FIELDS = ["id","created_time","from","to","message"]
	
class Note(PyFacebook,Object,Connection,Comments,Likes):
	#http://developers.facebook.com/docs/reference/api/note/
	CONN = ["comments","likes"]
	FIELDS = ["id","from","subject","message","comments","created_time",
			"updated_time","icon"]
	
class Page(PyFacebook,Object,Connection,Man_event,Feed,Man_note,UploadFiles,Man_album):	
	#http://developers.facebook.com/docs/reference/api/page/
	CONN = ["feed","picture","settings","tagged","links","photos","groups",
			"albums","statuses","videos","notes","posts","events","checkins",
			"admins","blocked","tabs"]
	FIELDS = ["id","name","link","category","likes","location","phone","checkins",
			"access_token"]
	
	def get_blocked_list(self):
		"""get a list of users blocked"""
		return self.Request(method="blocked")
	
	def is_blocked(self,id):
		"""check if a user is blocked"""
		return self.Request(method="blocked/%s" % id)		
	
	def block_user(self,u_id):
		"""block a user"""
		return self.Request( method ="blocked" , post ={"uid":u_id})	
	
	def unblock_user(self,u_id):
		"""unblock a blocked user"""
		return self.Request(delete=True,method ="blocked/%s" % u_id)
	
	def read_tab(self,parameter,tab_id=""):
		"""read the tabs"""
		return self.Request(method="tabs/%s" % tab_id)
	
	def create_tab(self,app_id):
		"""install a profile_tab"""
		return self.Request( method ="tabs" , post={"app_id",app_id})
	
	def update_tab(self,tab_id,**args):
		"""update an installed profile_tab"""
		return self.Request( method ="tabs/%s"% (tab_id) , post=args)
	
	def delete_tab(self,tab_id):
		"""delete an installed profile_tab"""
		return self.Request(delete=True,method ="tabs/%s" % tab_id)
	
	def is_admin(self,id):
		"""Check if a specific user is an admin of the Page"""
		return self.Request(method="admins/%s" % id)
	
	def update_setting(self,setting,value):	
		"""change whether users can post to the Wall"""
		return self.Request( method ="settings" , post={"setting":setting,"value":value})
	
					
class Photo(PyFacebook,Object,Connection,Comments,Likes):	
	#https://developers.facebook.com/docs/reference/api/photo/
	CONN = ["comments","likes","picture","tags"]
	FIELDS = ["id","from","tags","name","icon","picture","source","height","width",
			"images","link","created_time","updated_time","position"]
	
	def tag_user(self,id,args=""):	
		return self.Request( method ="tags/%s" % (id) , post =args)
	
		
class Post(PyFacebook,Object,Connection,Comments,Likes):	
	#https://developers.facebook.com/docs/reference/api/post/
	CONN = ["comments","likes"]
	FIELDS = ["id","from","to","message","picture","link","name","caption","description",
			"source","properties","icon","actions","privacy","type","likes","comments","object_id",
			"application","created_time","updated_time","targeting"]
	
class Review(PyFacebook,Object):
	#https://developers.facebook.com/docs/reference/api/Review/
	FIELDS = ["id","from","to","message","rating","created_time"]	
	
class Status(PyFacebook,Object,Connection,Comments,Likes):
	#https://developers.facebook.com/docs/reference/api/status/
	CONN = ["comments","likes"]
	FIELDS = ["id","from","message","updated_time","type"]	
	
class Subscription(PyFacebook,Object):
	#https://developers.facebook.com/docs/reference/api/subscription/
	FIELDS = ["object","fields","callback_url"]
		
class Thread(PyFacebook,Object,Connection):
	#https://developers.facebook.com/docs/reference/api/thread/
	CONN = ["tags","participants","former_participants","senders","messages"]
	FIELDS = ["id","snippet","updated_time","message_count","unread_count","tags","participants",
			"former_participants","senders","messages"]				
		
class User(PyFacebook,Object,Connection,Man_album,Man_event,Feed,Man_friendlist,Likes,Man_note,UploadFiles):
	CONN = ["accounts","activities","adaccounts","albums","apprequests","books","checkins",
			"events","family","feed","friendlists","friendrequests","friends","games","groups","home",
			"inbox","interests","likes","links","movies","music","notes","notifications","outboxpayments",
			"permissions","photos","picture","posts","scores","statuses","tagged","television","updates","videos"]
	
	FIELDS = ["id","name","first_name","middle_name","last_name","gender","locale","languages","link","username",
			"third_party_id","timezone","updated_time","verified","bio","birthday","education","email","hometown",
			"interested_in","location","political","favorite_athletes","favorite_teams","quotes","relationship_status",
			"religion","significant_other","video_upload_limits","website","work"]
	

	def create_achievement(self,achievement):
		"""create an achievement for a user"""
		return self.Request(comp="achievements",post={"achievement":achievement})
	
	def delete_achievement(self,achievement):
		"""delete an achievement for a user"""
		return self.Request(delete=True,method ="achievements",post={"achievement":achievement})	
	
	def post_score(self,score):	
		"""post a score for a user"""
		return self.Request(comp="scores",post={"score":score})
	
	def is_liked(self,id):
		"""check if a User likes a specific page"""
		return self.Request(method="likes%s" % id)		
	
	def de_authorize_app(self,**args):
		"""de-authorize an application or revoke a specific extended permissions"""
		return self.Request(delete=True,method ="permissions",post=args)			
	
	def is_friend(self,id):			
		"""check if a User is a friend of the current session User"""
		return self.Request(method="friends/%s" % id)	
	
	def checkin(self,**args):
		"""checkin an user"""
		return self.Request( method ="checkins", post =args)	
	
	
class Video(PyFacebook,Object,Connection,Likes,Comments):
	CONN = ["likes","comments","picture"]
	FIELDS = ["id","from","tag","name","description","picture","embed_html","icon","source","created_time",
			"updated_time","comments"]
	
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
