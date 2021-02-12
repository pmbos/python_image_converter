import jwt
from datetime import datetime, timedelta

from api.shared.database import db
from configuration import config

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.username = name
        print('created user with name: ' + self.username)

    def commit_to_database(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_database(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def find_user_in_database(cls, user_name):
        return cls.query.filter_by(username=user_name).first()

    @classmethod
    def validate_user(cls, user_id: int):
        return cls.query.get(user_id)


class Admin(User):
    password = db.Column(db.String(150))

    def __init__(self, id, name, password):
        super().__init__(id, name)
        self.password = password

    def generate_user_token(self):
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=0, minutes=1),
                'iat': datetime.utcnow(),
                'sub': self.id
            }

            return jwt.encode(
                payload,
                config.CONFIG_AUTH_SECRET_KEY_JWT,
                algorithm='HS256'
            )

        except Exception:
            print('Could not return JWT token!')

    @staticmethod
    def decode_auth_token(_, token):
        try:
            payload = jwt.decode(token, config.CONFIG_AUTH_SECRET_KEY_JWT)
            return payload.get('sub', None)
        except jwt.ExpiredSignatureError:
            print('Token expired. New login required!')
        except jwt.InvalidTokenError:
            print('Token was invalid. Please log in!')
        return None

    @staticmethod
    def validate_auth_token(cls, token):
        decoded_token = cls.decode_auth_token(cls, token)

        if decoded_token is None:
            return False
        
        user_with_token = User.query.get(decoded_token)

        if user_with_token is None:
            return False
        return True
