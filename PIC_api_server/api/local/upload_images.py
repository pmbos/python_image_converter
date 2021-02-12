import os
from flask import Blueprint, request

from PIC_api_server.configuration import config
from PIC_api_server.api.shared import _save_images_to_input_dir, _invoke_Python_Image_Converter, User
from PIC_api_server.api.shared import RootAccessAttemptedError

local_image_converter = Blueprint('images', __name__)


@local_image_converter.before_request
def check_payload():
    data = request.get_json()
    if data is None:
        return 'Data was not in JSON format!', 500


@local_image_converter.route('/local/convert_images', methods=['POST'])
def upload_images():
    data = request.get_json()
    try:
        images = data.get(config.CONFIG_JSON_IMAGES)
        save_to, output = _check_authentication(data)
        show = config.CONFIG_PIG_SHOW_OUTPUT_WHEN_COMPLETE
        auto_clean = config.CONFIG_PIC_AUTO_CLEAN
        delete = config.CONFIG_PIC_DELETE_WHEN_AUTO_CLEAN
        sort = config.CONFIG_PIC_SORT_WHEN_AUTO_CLEAN

        if delete and sort:
            raise InvalidLocalConfiguration('It is not allowed to use the delete and sort flags at the same time.')

        _save_images_to_input_dir(images, save_to)
        _invoke_Python_Image_Converter((save_to, output, show, auto_clean, delete, sort))
    except InvalidLocalConfiguration as config_error:
        return config_error.message, 500
    except  LocalUserDoesNotExistError as non_existing_user_error:
        return non_existing_user_error.message, 500
    except RootAccessAttemptedError as root_error:
        return root_error.message, 500

    return 'Images Converted!', 200


def _check_authentication(json_data):
    '''
    Check if local authentication should be used and return a path based on whether it should or not.
    :param: json_data, the JSON data obtained from the request.
    :return: str, the path to save the converted images to.
    '''
    base_source_path = os.path.realpath(config.CONFIG_PIC_SOURCE_DIR)
    base_output_path = os.path.realpath(config.CONFIG_PIC_OUTPUT_DIR)

    if config.CONFIG_USE_LOCAL_AUTHENTICATION:
        user_id = json_data.get(config.CONFIG_JSON_USER_ID, None)
        user_name = json_data.get(config.CONFIG_JSON_USER_NAME)
        id_not_none = user_id is not None

        if id_not_none:
            found_user = User.query.get(user_id) is not None
        else:
            found_user = User.query.filter_by(username=user_name) is not None
    
        if found_user:
            save_to = os.path.join(base_source_path, str(user_name))
            output = os.path.join(base_output_path, str(user_name))

            if user_name == config.CONFIG_AUTH_ROOT_USERNAME:
                raise RootAccessAttemptedError('The root user may not operate the API')
            if not os.path.isdir(save_to):
                os.mkdir(save_to)
            if not os.path.isdir(output):
                os.mkdir(output)
            
            return save_to, output
        else:
            raise LocalUserDoesNotExistError('The local user provided in the request does not exist.')
    else:
        return base_source_path, base_output_path


class LocalAPIError(Exception):
    def __init__(self, message):
        self.message = message

class InvalidLocalConfiguration(LocalAPIError):
    def __init__(_, message):
        super().__init__(message)

class LocalUserDoesNotExistError(LocalAPIError):
    def __init__(_, message):
        super().__init__(message)
