import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from pathlib import Path

LOG_DIR = Path(__file__).parent
LOG_DIR.mkdir(exist_ok=True)

def setup_logger():
    log_queue = Queue()

    file_handler = logging.FileHandler(
        LOG_DIR / "tnb_torre.log",
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        "%d/%m/%Y %H:%M:%S"
    )
    file_handler.setFormatter(formatter)

    queue_handler = QueueHandler(log_queue)

    logger = logging.getLogger("tnb")
    logger.setLevel(logging.INFO)
    logger.addHandler(queue_handler)

    listener = QueueListener(log_queue, file_handler)
    listener.start()

    return logger, log_queue, listener