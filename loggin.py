import logging

def setup_logging():
    logging.basicConfig(filename='progress.log', level=logging.INFO, 
                        format='%(asctime)s:%(levelname)s:%(message)s')

def log_message(message, level='info'):
    if level == 'info':
        logging.info(message)
    elif level == 'error':
        logging.error(message)
    elif level == 'warning':
        logging.warning(message)

setup_logging()
log_message("Hayooo rabba")
log_message("baab re baap","error")
