import logging

logging.basicConfig(filename="worker.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')
logger = logging.getLogger('worker_logger')
logger.setLevel(logging.DEBUG)

def getLogger():
    return logger
    