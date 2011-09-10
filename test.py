#!/usr/bin/python

import pyfacebook
try:
	from pyfacebook.common import *
except ImportError: 
	album_id = ""
	app_id = ""
	app_secret = ""

permission = ["read_mailbox","user_photos","publish_stream","user_checkins","friends_checkins","publish_checkins","rsvp_event","read_stream","read_friendlists","manage_friendlists","user_groups","friends_groups","offline_access"]

#init library
pyfacebook.init(access_token=access_token,app_id=app_id,permission=permission)

#Post 4 links
print pyfacebook.User("me").create_post({"link":"http://www.google.it","message":"test"})
print pyfacebook.User("me",access_token).create_post({"link":"http://www.google.it","message":"test"})
print pyfacebook.Feed("me").create_post({"link":"http://www.google.it","message":"test"})
print pyfacebook.Feed("me",access_token).create_post({"link":"http://www.google.it","message":"test"})

print pyfacebook.User("me").object()
print pyfacebook.Object("me").object()

#print the profile that created this album and the title of the album 
print "print the profile that created this album and the title of the album "
print pyfacebook.Album(album_id).object(fields=["from","name"])
#The photos contained in this album
print "The photos contained in this album"
print pyfacebook.Album(album_id,access_token).connection("photos")

#The album's cover photo
print "The album's cover photo"
f = open("test.jpg","w")
f.write(pyfacebook.Connection(album_id,access_token).connection("picture"))
f.close()


#Add comment to an album
print "Add comment to an album"
ret = pyfacebook.Album(album_id).comment('test')
print ret
#like a comment
print "like a comment"
print pyfacebook.Likes(ret['id']).like()
#unlike an Album
print "unlike an Album"
print pyfacebook.Album(album_id).unlike()

#The photo albums this page has created
print "The photo albums this page has created"
print pyfacebook.Application("2439131959").connection("albums")
print pyfacebook.Application("2439131959").connection("albums",limit=25,until=1247270845)
# =
print pyfacebook.GetRequest().get_request("https://graph.facebook.com/2439131959/albums?access_token=%s&limit=25&until=1247270845" % (access_token))


#Create a test account for an application
print "Create a test account for an application"
test_user = pyfacebook.Application(app_id,pyfacebook.get_client_access_token(app_id, app_secret)).create_account(parameter={"name":"lolasd","installed":True})
print test_user

#Ban a user
print pyfacebook.Application(app_id,pyfacebook.get_client_access_token(app_id, app_secret)).ban_user(test_user["id"])
#Get  a list of banned users
print pyfacebook.Application(app_id,pyfacebook.get_client_access_token(app_id, app_secret)).get_list()
#Delete a test account for an application
print "Delete a test account for an application"
print pyfacebook.Application(test_user["id"],pyfacebook.get_client_access_token(app_id, app_secret)).delete_account()

#Add photos to an album
print "Add photos to an album"
files = [{"filename":"./util/image.jpg","message":"Uploaded with PyFbGraph!1"}]
print pyfacebook.Album(album_id).upload_photo(files)
#RSVP the user as 'attending' an Event
print pyfacebook.Event("225986690757733").attending()

#Create a Friendlist
list = pyfacebook.Friendlist("me").create("Name")
#Add a user to a FriendList
print pyfacebook.Friendlist(list["id"]).add_member("Friend ID")
#Get all of the users who are members of this list.
print pyfacebook.Friendlist(list["id"]).connection("members")
#Remove a user from a FriendList
print pyfacebook.Friendlist(list["id"]).remove_member("Friend ID")
#Delete a Friendlist
print pyfacebook.Friendlist(list["id"]).delete()