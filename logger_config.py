import logging
import os.path
import datetime

def setup_logger():
    log_dir = 'logs'
    log_file = os.path.join(log_dir, f'delivery_{datetime.datetime.now().strftime("%d%m%Y")}.log')
    logging.basicConfig(level=logging.INFO,
                        handlers=[
                            logging.FileHandler(log_file),
                            logging.StreamHandler()
                        ])
    return logging.getLogger(__name__)


logger = setup_logger()
