import os, sys

from configuration import config
from api.shared import Image

def _invoke_Python_Image_Converter(options: tuple):
    '''
    Parse the options and invoke the Python Image Converter with the relevant arguments.\n
    Use the currently running python executable to invoke PIC.
    :param: options, a tuple of options organised like (source, output, show, auto_clean, delete, sort)
    '''
    source = options[0]
    output = options[1]
    show = options[2]
    auto_clean = options[3]
    delete = options[4]
    sort = options[5]

    arguments = f'-i {source} -o {output}'
    if not show:
        arguments += f' --noshow'
    if auto_clean:
        arguments += f' --auto'
    if delete:
        arguments += f' --delete'
    if sort:
        arguments += f' --sort'

    os.system(f'{sys.executable} {os.path.realpath(config.CONFIG_PIC_ROOT_SCRIPT)} {arguments}' )


def _save_images_to_input_dir(images, path):
    '''
    Save uploaded images to the PIC input directory.
    :param: images, the list of name, base64 lists of images [[image_name, base64 representation],...]
    :param: path, the path to save the images to.
    '''
    decoded_images = []

    for image_data in images:
        image_name = image_data.get(config.CONFIG_JSON_IMAGE_NAME)
        image_bytes = image_data.get(config.CONFIG_JSON_IMAGE_DATA).encode('utf-8')
        decoded_images.append(Image.decode_base_64(image_bytes, image_name, path))

    return decoded_images