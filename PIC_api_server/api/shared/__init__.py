from api.shared.image import Image
from api.shared.database import db
from api.shared.run_pic import _invoke_Python_Image_Converter, _save_images_to_input_dir
from api.shared.user import User, Admin

class SharedAPIError(Exception):
    def __init__(self, message):
        self.message = message

class RootAccessAttemptedError(SharedAPIError):
    def __init__(_, message):
        super().__init__(message)