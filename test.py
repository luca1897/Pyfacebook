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

#print the profile that created this album and the title of the album 
print pyfacebook.Album().object(album_id,fields=["from","name"])
data = pyfacebook.Album().connections([{"id":album_id,"connection":"photos"},{"id":album_id,"connection":"picture"}])

#The photos contained in this album
print data[0]

#The album's cover photo
f = open("test.jpg","w")
f.write(data[1])
f.close()

#Add photos to an album
files = [{"filename":"./util/image.jpg","message":"Uploaded with PyFbGraph!1"}]
print pyfacebook.Album().upload_photo(album_id,files)

#Add comment to an album
print pyfacebook.Album().comment(album_id,"test")
#like an Album
print pyfacebook.Album().like(album_id)
#unlike an Album
print pyfacebook.Album().unlike(album_id)

#The photo albums this page has created
print pyfacebook.Application().connection("2439131959","albums")
print pyfacebook.Application().connection("2439131959","albums",limit=25,until=1247270845)
# =
print pyfacebook.GetObject().get_object("https://graph.facebook.com/2439131959/albums?access_token={ACCESSTOKEN}&limit=25&until=1247270845")

client_access_token = pyfacebook.get_client_access_token(app_id, app_secret)
print client_access_token
#Create a test account for an application
print pyfacebook.Application().create_account(app_id, client_access_token, parameter={"name":"lolasd","installed":True})
#Delete a test account for an application
print pyfacebook.Application().delete_account("id test user",client_access_token)