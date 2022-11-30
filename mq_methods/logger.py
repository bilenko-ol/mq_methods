import logging

level = logging.getLevelName('DEBUG')

logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

worker_logger = logging.getLogger('mq.worker')
client_logger = logging.getLogger('mq.client')
