import sys, getopt

from flask import Flask
from werkzeug import security

from PIC_api_server.api import db
from PIC_api_server.api.local import local_image_converter
from PIC_api_server.api.shared import Admin
from PIC_api_server.authentication import create_users_blueprint
from PIC_api_server.authentication import authenticate_user

from PIC_api_server.configuration import config


def create_app(argv):
    '''
    Create a Flask web app to host the API.
    :param: The arguments passed to the application.
    :return: a Flask web app instance.
    '''
    # Configuration
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.CONFIG_DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Parse arguments
    api = parse_arguments(argv)

    # Blueprints
    if api == config.ARGV_LOCAL_API_LONG:
        app.register_blueprint(local_image_converter, url_prefix='/api')

    app.register_blueprint(create_users_blueprint, url_prefix='/auth')
    app.register_blueprint(authenticate_user, url_prefix='/auth')

    # Database
    with app.app_context():
        db.init_app(app)
        if config.CONFIG_DB_CLEAR:
            db.drop_all()
        db.create_all(app=app)

        root_user = Admin.query.get(0)
        if root_user is None:
            db.session.add(Admin(0, 
            config.CONFIG_AUTH_ROOT_USERNAME, 
            security.generate_password_hash(config.CONFIG_AUTH_ROOT_PASSWORD))
            )
            db.session.commit()

    return app


def usage():
    '''
    The usage definition of the app.
    :return: The usage string.
    '''
    return 'Usage: python app.py [-l/--local] [-w/--web]'


def parse_arguments(argv):
    '''
    Parse the arguments passed to the application.
    :param: The arguments passed to the application.
    :return: The API configuration.
    '''
    # Setup option strings/lists and parse arguments.
    help = usage()
    try:
        option_string = f'{config.ARGV_LOCAL_API}{config.ARGV_WEB_API}'
        long_options = [ 
            config.ARGV_LOCAL_API_LONG,
            config.ARGV_WEB_API_LONG
        ]
    
        options, _ = getopt.getopt(argv, option_string, long_options)
    except getopt.GetoptError:
        print(f'Invalid arguments! {help}')
        sys.exit(2)

    if config.CONFIG_SUPERCEEDS_ARGUMENTS:
        return config.CONFIG_API_TO_USE
    elif len(options) == 0:
        print(help)
        sys.exit(2)
    elif len(options) > config.CONFIG_NUMBER_OF_VALID_ARGUMENTS:
        print('Please do not use more arguments than is allowed')
        print(help)
        sys.exit(2)
    else:
        for option in options:
            if option in (f'--{config.ARGV_LOCAL_API_LONG}', f'-{config.ARGV_LOCAL_API}'):
                config.CONFIG_API_TO_USE = config.ARGV_LOCAL_API_LONG
            elif option in (f'--{config.ARGV_WEB_API_LONG}', f'-{config.ARGV_WEB_API}'):
                config.CONFIG_API_TO_USE = config.ARGV_WEB_API_LONG
            else:
                print('Unknown argument!')
                print(help)
                sys.exit(2)

    return config.CONFIG_API_TO_USE


def main(argv):
    '''
    The root function of the application.
    :param: The arguments passed to the application.
    '''
    app = create_app(argv)
    app.run()

# ================Boot Condition================
if __name__ == '__main__':
    main(sys.argv[1:])
