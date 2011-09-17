#!/usr/bin/python
import time
import pyfacebook
try:
	from pyfacebook.common import *
except ImportError: 
	album_id = ""
	app_id = ""
	app_secret = ""
	page_id = ""
	photo_id = ""

permission = ["publish_actions","user_likes","read_mailbox","user_photos","publish_stream","user_checkins","friends_checkins","publish_checkins","rsvp_event","read_stream","read_friendlists","manage_friendlists","user_groups","friends_groups","offline_access","create_event"]

#init library
pyfacebook.init(access_token=access_token,app_id=app_id,permission=permission) 
print pyfacebook.get_generic_access_token()

print pyfacebook.User("me").object()

#print the profile that created this album and the title of the album 
print "print the profile that created this album and the title of the album "
print pyfacebook.Album(album_id).object(fields=["from","name"])
#The photos contained in this album
print "The photos contained in this album"
print pyfacebook.Album(album_id,access_token).connection("photos")

#The album's cover photo
print "The album's cover photo"
f = open("test.jpg","w")
f.write(pyfacebook.Album(album_id,access_token).connection("picture"))
f.close()


#Add comment to an album
print "Add comment to an album"
ret = pyfacebook.Album(album_id).comment('test')
print ret
#like a comment
print "like a comment"
print pyfacebook.Album(ret['id']).like()
#unlike an Album
print "unlike an Album"
print pyfacebook.Album(album_id).unlike()

#The photo albums this page has created
print "The photo albums this page has created"
print pyfacebook.Application("2439131959").connection("albums")
print pyfacebook.Application("2439131959").connection("albums",limit=25,until=1247270845)
# =

#Add photos to an album
print "Add photos to an album"
files = [{"filename":"./util/image.jpg","param":{"message":"Uploaded with PyFbGraph!1"}}]
print pyfacebook.Album(album_id).upload_files(files)


#Create a Friendlist
list = pyfacebook.Friendlist("me").create_friendlist("Name")
#Add a user to a FriendList
print pyfacebook.Friendlist(list["id"]).add_member(friend_id) 
#Get all of the users who are members of this list.
print pyfacebook.Friendlist(list["id"]).connection("members")
#Remove a user from a FriendList
print pyfacebook.Friendlist(list["id"]).remove_member(friend_id)
#Delete a Friendlist
print pyfacebook.Friendlist(list["id"]).delete_friendlist()



#Create an event

#Parameter	 	Description	 			Type	 													Required
#name			Event name				string	 													yes
#start_time		Event start time	 	UNIX timestamp					 							yes
#end_time		Event end time	 		UNIX timestamp	 											no
#message			Event description		string	 													no
#location	 	Event location			string	 													no
#privacy_type	Event privacy setting	string containing 'OPEN' (default), 'CLOSED', or 'SECRET'	no

print pyfacebook.Man_event("me").create_event(name="test",start_time=int(time.time()))

#USERS_CAN_POST, USERS_CAN_POST_PHOTOS, USERS_CAN_TAG_PHOTOS, USERS_CAN_POST_VIDEOS
print pyfacebook.Page(page_id,page_access_token).update_setting("USERS_CAN_POST",True)

#Post a link
print pyfacebook.User("me").create_post({"link":"http://www.google.it","message":"test"})


#tag an user on the photo
print pyfacebook.Photo(photo_id).tag_user(me_id,{"x":"70","y":"50"})

comment_id = pyfacebook.Photo(photo_id).comment("test")["id"]
print pyfacebook.Photo(comment_id).del_comment()
print pyfacebook.User("me").connection("groups")


print pyfacebook.User(me_id,pyfacebook.get_client_access_token(app_id, app_secret)).post_score("30")

print pyfacebook.User(me_id).is_liked("19292868552")

#Create a test account for an application
print "Create a test account for an application"
test_user = pyfacebook.Application(app_id,pyfacebook.get_client_access_token(app_id, app_secret)).create_account(name = "lolasd",installed=True)
print test_user

#Ban a user
print "Ban a user"
print pyfacebook.Application(app_id,pyfacebook.get_client_access_token(app_id, app_secret)).ban_user(test_user["id"])
#Get  a list of banned users
print "a list of banned users"
print pyfacebook.Application(app_id,pyfacebook.get_client_access_token(app_id, app_secret)).get_banned_list()

#un-ban a user account
print "un-ban a user account"
print pyfacebook.Application(app_id,pyfacebook.get_client_access_token(app_id, app_secret)).unban_user(test_user["id"])

#Delete a test account for an application
print "Delete a test account for an application"
print pyfacebook.Application(test_user["id"],pyfacebook.get_client_access_token(app_id, app_secret)).delete_account()

#RSVP the user as 'maybe' an Event
print pyfacebook.Event("225986690757733").maybe()





