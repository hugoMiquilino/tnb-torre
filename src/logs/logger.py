import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from pathlib import Path
import os


def get_log_dir():
    base = Path(os.getenv("LOCALAPPDATA", Path.home()))
    log_dir = base / "TNB-Torre" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logger():
    log_queue = Queue()

    log_dir = get_log_dir()
    log_file = log_dir / "tnb_torre.log"

    file_handler = logging.FileHandler(
        log_file,
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
    logger.handlers.clear()      # 🔥 evita handlers duplicados
    logger.addHandler(queue_handler)

    listener = QueueListener(log_queue, file_handler)
    listener.start()

    return logger, log_queue, listener
