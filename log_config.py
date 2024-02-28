# log_config.py
import logging
import os


def setup_logging():
    """
    Setup the logging configuration
    """
    log_directory = "/tmp/ssh_logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file_path = os.path.join(log_directory, 'app.log')
    # if the file exists, delete it
    if os.path.exists(log_file_path):
        os.remove(log_file_path)

    logging.basicConfig(
        filename=log_file_path,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
