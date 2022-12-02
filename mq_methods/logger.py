import logging
import os

level = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO'))

logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

worker_logger = logging.getLogger('mq.worker')
client_logger = logging.getLogger('mq.client')
