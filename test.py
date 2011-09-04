import pyfacebook
try:
	from pyfacebook.common import *
except ImportError: 
	album_id = ""
	app_id = ""

files = [{"filename":"./util/image.jpg","message":"Uploaded with PyFbGraph!1"}]
permission = ["read_mailbox","user_photos","publish_stream","user_checkins","friends_checkins","publish_checkins","rsvp_event","read_stream","read_friendlists","manage_friendlists","user_groups","friends_groups","offline_access"]

pyfacebook.init(access_token=access_token,app_id=app_id,permission=permission)
print pyfacebook.Album().upload_photo(album_id,files)