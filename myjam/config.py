import os
SQLALCHEMY_DATABASE_URI = 'set in local config'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = '9\x85\x96z\xa5\x1e<\xbd\x8b\x08b\x0f\x8a\xe6#W\xf5]\x10\xe1_L\xc6\x17'
DEBUG = True

UPLOAD_PATH = '/tmp/pictures'

BRYPT_LOG_ROUNDS = 12

SECURITY_REGISTERABLE = True
SECURITY_CONFIRMABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_TOKEN_MAX_AGE = 86400 #24 hours
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'whysosalty?'

FOOD2FORK_API_KEY = 'set in local config'
FOOD2FORK_SEARCH_URL = 'http://food2fork.com/api/search'
FOOD2FORK_GET_URL = 'http://food2fork.com/api/get'
FOOD2FORK_USE_CACHE = False
FOOD2FORK_CACHE_EXPIRE_AFTER = 200


# Set mail configuration in user config file
# MAIL_SERVER = 'smtp.myserver.com'
# MAIL_PORT = 465
# MAIL_USE_SSL = True
# MAIL_USERNAME = 'myusername'
# MAIL_PASSWORD = 'mypassword'
