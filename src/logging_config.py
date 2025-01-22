import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG to include debug messages, INFO for general use
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("process_log.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )