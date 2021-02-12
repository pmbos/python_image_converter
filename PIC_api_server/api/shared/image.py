import os
import base64

from api.shared.database import db

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text, nullable=False, unique=True)
    '''An image class for storing image data'''
    def __init__(self, name='', path='') -> None:
        '''
        Initialise the Image class
        :param: name (optional), the name of the image. Default: empty string
        :param: path (optional), the path at which the image is located. Default: empty string
        '''
        self.name = name
        self.path = path

    def __repr__(self) -> str:
        return f'<Image name={self.name}, path={self.path}/>'

    def encode_base_64(self) -> str:
        '''
        Encode the image as Base64
        :return: a UTF-8 representation of the Base64 encoding.
        '''
        result = None
        with open(self.path, 'rb') as binary_file:
            file_data = binary_file.read()
            base_64_encoded_data = base64.b64encode(file_data)
            result = base_64_encoded_data.decode('utf-8')
        return result

    @classmethod
    def decode_base_64(_, base64_data: bytes, name: str, write_to: str=''):
        '''
        Decode Base64 data into a new image file.
        :param: base64_data, the byte Base64 data.
        :param: name, the name of the file you want to create.
        :param: write_to (optional), the path to save the file to.
        :return: a new Image instance with the given name for its name and the constructed path
        for its path.
        '''
        write_to_path = os.path.join(write_to, name)
        with open(write_to_path, 'wb') as file_to_save:
            decoded_image_data = base64.decodebytes(base64_data)
            file_to_save.write(decoded_image_data)

        return Image(name=name, path=write_to_path)
