from flask import Blueprint, request
from werkzeug.security import generate_password_hash

from PIC_api_server.api.shared import User, Admin
from PIC_api_server.configuration import config


create_users_blueprint = Blueprint('create_users', __name__)


@create_users_blueprint.before_request
def authenticate():
    json_data = request.get_json()

    if json_data is None:
        return 'No user data was provided', 200

    auth_token = json_data.get(config.CONFIG_JSON_AUTH_TOKEN)
    if not Admin.validate_auth_token(Admin, auth_token):
        return 'Authentication token was invalid, please log in again.', 200



@create_users_blueprint.route('/create_users', methods=['POST'])
def create_users():
    data = request.get_json()

    users = data.get(config.CONFIG_JSON_REGISTER_USERS)
    for user in users:
        user_id = user.get(config.CONFIG_JSON_USER_ID, None)
        user_name = user.get(config.CONFIG_JSON_USER_NAME).lower()
        new_user = User(user_id, user_name)
        new_user.commit_to_database()
        if User.query.filter_by(username=user_name) is None:
            return 'User not created', 500
            
    print('Correctly created users!')
    return 'Users created', 200



@create_users_blueprint.route('/create_admins', methods=['POST'])
def create_admins():
    data = request.get_json()

    users = data.get(config.CONFIG_JSON_REGISTER_USERS)
    for user in users:
        user_id = user.get(config.CONFIG_JSON_USER_ID, None)
        user_name = user.get(config.CONFIG_JSON_USER_NAME)
        user_password = user.get(config.CONFIG_JSON_USER_PASSWORD)
        new_admin = Admin(user_id, user_name, user_password)
        new_admin.commit_to_database()
        if Admin.query.filter_by(username=user_name) is None:
            return 'Admin not created', 500
            
    print('Correctly created admins!')
    return 'Admins created', 200
