import os
import cv2 as cv
import numpy as np
import datetime as dt
import logging

class PIC:
    '''Python Image Converter: Responsible for loading, converting and saving images from source to target.'''
    ACCEPTABLE_IMAGE_TYPES = ['jpg', 'png', 'jpeg']
    BASE_SOURCE_DIR = './images/'
    BASE_TARGET_DIR = './converted_images/'
    _TIMESTAMP_FORMAT = '%B_%d_%Y-%H_%M_%S'

    def __init__(self, logger=None, path_to_images: str=BASE_SOURCE_DIR, target: str=BASE_TARGET_DIR, 
        delete_source_file_when_complete: bool=True, organise_source_files_when_complete: bool=False,
        auto_cleanup: bool=False):
        '''
        Initialise the Python Image Converter and validate source and target directories.
        :param: logger, the logger to use
        :param: path_to_images, the source directory from which to take images.
        :param: target, the target directory to save images to.
        :param: delete_source_file_when_complete, a flag indicating whether to delete the original 
        source files upon completion of conversion process.
        :param: organise_source_files_when_complete, a flag indicating whether to automatically sort source files 
        upon completion of the conversion process.
        '''
        self.path = path_to_images
        self.target = target
        self.image_paths = []
        self.auto_delete = delete_source_file_when_complete
        self.auto_organise = organise_source_files_when_complete
        self.auto_cleanup = auto_cleanup
        self.logger = logger

        self.log(self.path, logging.INFO)
        self.log(self.target, logging.INFO)

        if self.auto_delete == self.auto_organise and self.auto_delete:
            raise ConflictingCompletionActionsError('Please set at least one of either delete_source_file_when_complete or organise_source_files_when_complete to False')

        self._validate_source_and_target_directories()

    def convert_to_paintable(self):
        '''
        Convert an image to its black-and-white equivalent common to drawing books.\n
        Converted images will be saved to the target directory.
        '''
        for root, file in self.image_paths:
            image = self.read_image(os.path.join(root, file))
            grayscale_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            median_blur = cv.medianBlur(grayscale_image, 5)
            thresholded_image = self.apply_adaptive_thresholding(median_blur)
            
            timestamp = dt.datetime.now().strftime(self._TIMESTAMP_FORMAT)
            self.save_image(thresholded_image, f'paintable-contours-{timestamp}-{file}')

        if self.auto_cleanup:
            self.clean_up()

    def convert_to_laplacian(self):
        '''Convert an image to a chalk drawing.'''
        for root, file in self.image_paths:
            image = self.read_image(os.path.join(root, file))
            grayscale = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            lap = cv.Laplacian(grayscale, cv.CV_64F, ksize=3)
            lap = np.uint8(np.absolute(lap))

            timestamp = dt.datetime.now().strftime(self._TIMESTAMP_FORMAT)
            self.save_image(lap, f'chalk-{timestamp}-{file}')

        if self.auto_cleanup:
            self.clean_up()
    
    @classmethod
    def apply_adaptive_thresholding(_, image, method=cv.ADAPTIVE_THRESH_GAUSSIAN_C):
        '''
        Apply adaptive thresholding to find the optimal threshold for edge detection.
        :param: image, a cv2, grayscale, preprocessed image to find thesholds for.
        :param: method (optional), the method of adaptive thresholding to use. \n
        Options: cv2.ADAPTIVE_THRESH_GAUSSIAN_C (default) or cv2.ADAPTIVE_THRESH_MEAN_C)) 
        :return: a thresholded image using: colour 255, given method, binary conversion, range 9 and correction 3
        '''
        colour_code = 255
        thresholding_method = method
        thresholding_format = cv.THRESH_BINARY
        thresholding_range = 9
        correction_constant = 3

        return cv.adaptiveThreshold(image, colour_code, thresholding_method, 
            thresholding_format, thresholding_range, correction_constant)

    @classmethod
    def scale_image(_, image, scale=0.75):
        '''
        Scale an image.
        :param: image, a cv2 image to scale.
        :param: scale (optional), the scaling factor. Options: range 0-1, default 0.75
        :return: a resized images using scale as the scaling factor.
        '''
        height = int(image.shape[0] * scale)
        width = int(image.shape[1] * scale)
        dimensions = (width, height)

        return cv.resize(image, dimensions, interpolation=cv.INTER_AREA)

    @classmethod
    def read_image(_, path: str):
        '''
        Read an image.
        :param: path, the path to read the image from.
        :return: a cv2 image that was read from the given path in BGR colour scheme.
        '''
        return cv.imread(path)

    def load_images(self):
        '''Attempt to load images from the source directory.'''
        try:
            for file in os.listdir(self.path):
                acceptable_files = [ (self.path, file) for ext in PIC.ACCEPTABLE_IMAGE_TYPES if file.endswith(ext) ]
                self.image_paths.extend(acceptable_files)
        except OSError:
            raise NoImagesFoundError('An error occurred whilst navigating the given directory, did you provide a valid directory?')
    
        if len(self.image_paths) == 0:
            raise NoImagesFoundError('No images in given directory!')

        self.log(f'{len(self.image_paths)} image(s) found!', logging.INFO)

    def save_image(self, image, file_name: str):
        '''
        Save an image.
        :param: image, the cv2 image to save.
        :param: file_name, the name of the output file. \n
        Images are saved to the target directory.
        '''
        try:
            name, ext = os.path.splitext(file_name)
            if ext != 'jpg':
                ext = 'jpg'

            cv.imwrite(os.path.join(self.target, f'{name}.{ext}'), image)
        except Exception:
            raise SaveError(f'Could not save file: {image}. Please, check if you are using one of these formats: {PIC.ACCEPTABLE_IMAGE_TYPES}')
        
        self.log(f'Successfully saved file: {file_name}', logging.INFO)

    def clean_up(self):
        '''Clean up the source directory if desired.'''
        dir_name = None
        for file in os.listdir(self.path):
            if not os.path.isfile(os.path.join(self.path, file)):
                continue

            if self.auto_delete:
                os.remove(os.path.join(self.path, file))
            elif self.auto_organise and dir_name is None:
                now = dt.datetime.now()
                dir_name = now.strftime('%B %d %Y %H %M %S')
                os.mkdir(os.path.join(self.path, dir_name))
                os.replace(os.path.join(self.path, file), os.path.join(self.path, dir_name, file))
            elif self.auto_organise and dir_name is not None:
                os.replace(os.path.join(self.path, file), os.path.join(self.path, dir_name, file))
            else:
                break

    def _validate_source_and_target_directories(self):
        '''PRIVATE METHOD: validate the given source and target directories.'''
        self.logger.info('Validating source and target directories...')
        if not os.path.isdir(self.path) or not os.path.isdir(self.target):
            self.logger.warning('Either source or target directory does not exist, attempting to create given locations...')
            if os.path.isdir(self.path):
                self.log('Validated source directory...', logging.INFO)
                self.log(f'Failed to validate target directory, attempting to create target directory at: {self.target}', logging.WARNING)
                try:
                    os.mkdir(self.target)
                except OSError:
                    raise FailedDirectoryCreationError(f'FATAL: failed to create target directory at: {self.target}. \nPlease check access rights to parent directory.')
            elif os.path.isdir(self.target):
                self.log('Validated target directory...', logging.INFO)
                self.log(f'Failed to validate source directory, attempting to create source directory at: {self.path}', logging.WARNING)
                try:
                    os.mkdir(self.path)
                except OSError:
                    raise FailedDirectoryCreationError(f'FATAL: failed to create source directory at: {self.path}. \nPlease check access rights to parent directory.')
            else:
                self.log('Could not validate either source or target directory. Attempting to create directories...', logging.WARNING)
                try:
                    os.mkdir(self.path)
                    os.mkdir(self.target)
                except OSError:
                    raise FailedDirectoryCreationError(f'FATAL: failed to create source and/or target directory at:\n {self.path} \n{self.target} \nPlease check access rights to parent directory.')
            
            self.log('Directory(-ies) created successfully!', logging.INFO)
        self.log('All directories OK!', logging.INFO)

    def log(self, message: str, level):
        '''
        Log a given message using the PIC's logger, if specified
        :param: message, the message to log.
        :param: level, the log level to use
        '''
        if self.logger is not None:
            self.logger.log(level, message)


class PICError(Exception):
    '''Base error for the Python Image Converter'''
    pass

class NoImagesFoundError(PICError):
    '''Error raised when no images were found in the source directory'''
    pass

class SaveError(PICError):
    '''Error raised when something goes wrong while saving an image'''
    pass

class FailedDirectoryCreationError(PICError):
    '''Error raised when a directory could not be created for a missing source or target directory'''
    pass

class ConflictingCompletionActionsError(PICError):
    '''Error raised when the clean-up actions conflict'''
    pass
