from configparser import ConfigParser

config = ConfigParser()
config.read("../auth.conf")

BASE_URL = config.get('Server', 'url')
DOMAIN = config.get('Server', 'project_space')
USERNAME = config.get('Server', 'user')
PASSWORD = config.get('Server', 'password')

MOBILE_USERNAME = config.get('Server', 'mobile_user')
MOBILE_PASSWORD = config.get('Server', 'mobile_password')
