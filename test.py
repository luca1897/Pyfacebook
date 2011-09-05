import pyfacebook
try:
	from pyfacebook.common import *
except ImportError: 
	album_id = ""
	app_id = ""

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