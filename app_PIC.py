import logging
import sys, getopt, os

from PIC.converter.pic import PIC, ConflictingCompletionActionsError, NoImagesFoundError, SaveError, FailedDirectoryCreationError

# =====================Command line argument definitions=====================
ARGV_HELP = 'h'
ARGV_HELP_LONG = 'help'
ARGV_INPUT = 'i'
ARGV_INPUT_LONG = 'input'
ARGV_OUTPUT = 'o'
ARGV_OUTPUT_LONG = 'output'
ARGV_CLEANUP_ORGANISE = 's'
ARGV_CLEANUP_ORGANISE_LONG = 'sort'
ARGV_CLEANUP_DELETE = 'd'
ARGV_CLEANUP_DELETE_LONG = 'delete'
ARGV_CLEANUP_AUTO = 'a'
ARGV_CLEANUP_AUTO_LONG = 'auto'
ARGV_COMPLETE_NO_SHOW = 'ns'
ARGV_COMPLETE_NO_SHOW_LONG = 'noshow'

# =====================Setup functions=====================
def setup_logger():
    '''Create a logger with a stream and file handler'''
    name = __name__
    if name == '__main__':
        name = 'PIC - Main'
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(os.path.realpath('./file.log'))

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)

    console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def usage():
    '''Construct the usage string'''
    usage_string = 'Usage: python app.py'
    usage_string += f' [-{ARGV_INPUT}/--{ARGV_INPUT_LONG} <source_directory>]'
    usage_string += f' [-{ARGV_OUTPUT}/--{ARGV_OUTPUT_LONG} <output_directory>]'
    usage_string += f' [-{ARGV_CLEANUP_DELETE}/--{ARGV_CLEANUP_DELETE_LONG}]'
    usage_string += f' [-{ARGV_CLEANUP_ORGANISE}/--{ARGV_CLEANUP_ORGANISE_LONG}]'
    usage_string += f' [-{ARGV_CLEANUP_AUTO}/--{ARGV_CLEANUP_AUTO_LONG}]'
    usage_string += f' [-{ARGV_COMPLETE_NO_SHOW}/--{ARGV_COMPLETE_NO_SHOW_LONG}]'
    usage_string += '\n'
    usage_string += f'Where -{ARGV_CLEANUP_DELETE} and -{ARGV_CLEANUP_ORGANISE} cannot be used simultaneously'
    
    return usage_string


def parse_arguments(argv, logger: logging.Logger):
    '''
    Parse command line arguments.
    :param: argv, the arguments passed to the application via the command line.
    :param: logger, the logger of the application.
    '''
    help = usage()

    # Setup option strings/lists and parse arguments.
    try:
        option_string = f'{ARGV_INPUT}:{ARGV_OUTPUT}:{ARGV_HELP}{ARGV_CLEANUP_DELETE}{ARGV_CLEANUP_ORGANISE}{ARGV_CLEANUP_AUTO}{ARGV_COMPLETE_NO_SHOW}'
        long_options = [ 
            ARGV_INPUT_LONG + '=', 
            ARGV_OUTPUT_LONG + '=',
            ARGV_HELP_LONG, 
            ARGV_CLEANUP_DELETE_LONG, 
            ARGV_CLEANUP_ORGANISE_LONG, 
            ARGV_CLEANUP_AUTO_LONG,
            ARGV_COMPLETE_NO_SHOW_LONG
        ]
    
        options, _ = getopt.getopt(argv, option_string, long_options)
    except getopt.GetoptError:
        logger.error(f'Invalid arguments! {help}')
        sys.exit(2)

    # Initialise resulting PIC arguments
    source_dir = None
    output_dir = None
    delete = False
    organise = False
    auto_cleanup = False
    no_show = False

    # Identify each option and its associated value
    for option, value in options:
        if option in (f'-{ARGV_HELP}', f'--{ARGV_HELP_LONG}'): # User asked for help
            logger.info(help)
            sys.exit(0)
        elif option in (f'-{ARGV_INPUT}', f'--{ARGV_INPUT_LONG}'): # User specified input directory
            source_dir = os.path.realpath(value)
        elif option in (f'-{ARGV_OUTPUT}', f'--{ARGV_OUTPUT_LONG}'): # User specified output directory
            output_dir = os.path.realpath(value)
        elif option in (f'-{ARGV_CLEANUP_DELETE}', f'--{ARGV_CLEANUP_DELETE_LONG}'): # User specified the delete cleanup flag
            if organise:
                logger.error('You cannot use the delete with the organise flag!')
                logger.info(help)
                sys.exit(2)
            
            delete = True
            organise = False
        elif option in (f'-{ARGV_CLEANUP_ORGANISE}', f'--{ARGV_CLEANUP_ORGANISE_LONG}'): # User specified the organise cleanup flag
            if delete:
                logger.error('You cannot use the organise with the delete flag!')
                logger.info(help)
                sys.exit(2)
            
            delete = False
            organise = True
        elif option in (f'-{ARGV_CLEANUP_AUTO}', f'--{ARGV_CLEANUP_AUTO_LONG}'): # User specified the auto cleanup flag
            auto_cleanup = True
        elif option in (f'-{ARGV_COMPLETE_NO_SHOW}', f'--{ARGV_COMPLETE_NO_SHOW_LONG}'): # User specified to noshow flag
            no_show = True
        
    return (no_show, source_dir, output_dir, delete, organise, auto_cleanup, logger) # Results


def open_in_explorer(path: str):
    '''Open a directory in the OS file explorer'''
    os.startfile(os.path.realpath(path))


def build_PIC(*args):
    '''
    Construct a Python Image Converter based on the given arguments.
    :param: args, the arguments to construct the Python Image Converter.
    '''
    if len(args) < 6:
        raise InvalidArgumentsError('One or more of the given arguments were invalid')

    if args[0] is None and args[1] is not None:
        return PIC(args[5], target=args[1], delete_source_file_when_complete=args[2], organise_source_files_when_complete=args[3], auto_cleanup=args[4])
    elif args[1] is None and args[0] is not None:
        return PIC(args[5], path_to_images=args[0], delete_source_file_when_complete=args[2], organise_source_files_when_complete=args[3], auto_cleanup=args[4])
    elif args[1] is not None and args[0] is not None:
        return PIC(args[5], path_to_images=args[0], target=args[1], delete_source_file_when_complete=args[2], organise_source_files_when_complete=args[3], auto_cleanup=args[4])
    else:
        return PIC(args[5], delete_source_file_when_complete=args[2], organise_source_files_when_complete=args[3], auto_cleanup=args[4])


def execute_completion_behaviour(no_show: bool, path: str, logger: logging.Logger):
    if path is None:
        path = os.path.realpath(PIC.BASE_TARGET_DIR)
    else:
        path = os.path.realpath(path)
    
    if not no_show:
        logger.info('Conversion complete! Opening target directory...')
        open_in_explorer(path)
    else:
        logger.info(f'Conversion complete! Files can be found at: {path}')



def main(argv):
    '''
    Entrypoint of the application.
    :param: argv, the command line arguments passed to the application.
    '''
    logger = setup_logger()
    parsed_arguments = parse_arguments(argv, logger)
    try:
        pic = build_PIC(*parsed_arguments[1:])
        pic.load_images()
        pic.convert_to_paintable()
    except InvalidArgumentsError:
        logger.error('One or more of the given arguments were invalid')
        logger.info(usage())
        sys.exit(2)
    except ConflictingCompletionActionsError:
        logger.error('You cannot use both the cleanup delete and cleanup organise flags, please use eiter one or the other')
        logger.info(usage())
        sys.exit(2)
    except NoImagesFoundError:
        logger.error('No images were found in the source directory!')
        logger.info(f'Please make sure you have images in the source directory, the default directory is: {PIC.BASE_SOURCE_DIR}')
        sys.exit(2)
    except SaveError:
        logger.error('Something went wrong while saving your images! Attempt running the application with elevated priviliges')
        sys.exit(2)
    except FailedDirectoryCreationError:
        logger.error('Failed to create source or target directory! Try running with elevated priviliges\nTry navigating to the directory of app.py\nIf this issue persists, specify the directories manually')
        sys.exit(2)

    execute_completion_behaviour(parsed_arguments[0], parsed_arguments[2], logger)


# =====================Errors=====================
class InvalidArgumentsError(Exception):
    pass


# =====================Application boot condition=====================
if __name__ == '__main__':
    main(sys.argv[1:])


