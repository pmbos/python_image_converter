# Config - Python Image Converter (PIC) - Feel free to change these settings
CONFIG_PIC_SOURCE_DIR = 'pic_src' # Can remain untouched if using an interface.
CONFIG_PIC_OUTPUT_DIR = 'pic_output' # Change this to where you want the app to output your converted images. (full path)
CONFIG_PIG_SHOW_OUTPUT_WHEN_COMPLETE = True # Shows you the output folder when the conversion is complete.
CONFIG_PIC_AUTO_CLEAN = True # Automatically cleans up source files (should be turned on if you are using an interface).
CONFIG_PIC_SORT_WHEN_AUTO_CLEAN = False # Sorts the source files
CONFIG_PIC_DELETE_WHEN_AUTO_CLEAN = True # Deletes the source files
CONFIG_PIC_ROOT_SCRIPT = './PIC/app.py' # PIC Python main script location

# Arguments - Any settings below here should not be changed
ARGV_LOCAL_API = 'l'
ARGV_LOCAL_API_LONG = 'local'
ARGV_WEB_API = 'w'
ARGV_WEB_API_LONG = 'web'

# Config - API server
CONFIG_SUPERCEEDS_ARGUMENTS = True
CONFIG_AVAILABLE_APIS = (ARGV_LOCAL_API_LONG, ARGV_WEB_API_LONG)
CONFIG_API_TO_USE = CONFIG_AVAILABLE_APIS[0]
CONFIG_NUMBER_OF_VALID_ARGUMENTS = 1
CONFIG_USE_LOCAL_AUTHENTICATION = False

# Config - API server JSON terms
CONFIG_JSON_IMAGES = 'Images'
CONFIG_JSON_IMAGE_NAME = 'ImageName'
CONFIG_JSON_IMAGE_DATA = 'Base64ImageData'
CONFIG_JSON_USER_ID = 'user_id'
CONFIG_JSON_USER_NAME = 'UserName'
CONFIG_JSON_USER_PASSWORD = 'user_password'
CONFIG_JSON_REGISTER_USERS = 'users'
CONFIG_JSON_TO_HASH = 'to_hash'
CONFIG_JSON_AUTH_TOKEN = 'auth_token'


# Config - API server authentication
CONFIG_AUTH_SECRET_KEY_JWT = '\x08Z\t}\xce\x9c\xdfr\xef\xc6\xc3!?\x06\x8f\xc1]\xbcxY$\xcatT'
CONFIG_AUTH_HASH_METHOD = 'SHA256'
CONFIG_AUTH_ROOT_USERNAME = 'ROOT'
CONFIG_AUTH_ROOT_PASSWORD = 'u\xb9#K7\xc7w\x80\x03;\x9e\t\xe0\x16\xea\x1d\x95Y\x8a\xe52\xe8\xe7\xe3'

# Config - Database
CONFIG_DB_PATH = 'data.db'
CONFIG_DB_CLEAR = False
