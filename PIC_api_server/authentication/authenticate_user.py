from flask import Blueprint, request, jsonify

from werkzeug import security

from PIC_api_server.configuration import config
from PIC_api_server.api.shared import Admin

authenticate_user = Blueprint('authenticate_user', __name__)


@authenticate_user.before_request
def check_payload():
    json_data = request.get_json()

    if json_data is None:
        return 'No JSON data found!', 200


@authenticate_user.route('/login', methods=['POST'])
def login():
    json_data = request.get_json()

    user_name = json_data.get(config.CONFIG_JSON_USER_NAME)
    user_password = json_data.get(config.CONFIG_JSON_USER_PASSWORD)

    all_users = Admin.query.all()

    to_log_in = None
    for user in all_users:
        if security.check_password_hash(user.username, user_name):
            to_log_in = user
            break

    if to_log_in is None:
        return 'User does not exist', 200
    
    if security.check_password_hash(to_log_in.password, user_password):
        user_token = to_log_in.generate_user_token()
        return jsonify(
            {
                config.CONFIG_JSON_AUTH_TOKEN: user_token.decode()
            }
        )
    return 'Incorrect password!', 200



@authenticate_user.route('/hash', methods=['POST'])
def generate_hash():
    json_data = request.get_json()
    to_hash = json_data.get(config.CONFIG_JSON_TO_HASH, None)

    if to_hash is None:
        return 'Could not find string to hash', 200

    return jsonify(
        {
            'hash': security.generate_password_hash(to_hash, method=config.CONFIG_AUTH_HASH_METHOD)
        }
    )
