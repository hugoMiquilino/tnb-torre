import logging
from datetime import datetime

class GuiLogHandler(logging.Handler):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def emit(self, record):
        try:
            timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
            level = record.levelname
            msg = record.getMessage()

            formatted = f"[{timestamp}] {msg}"
            self.queue.put(formatted)

        except Exception:
            self.handleError(record)
