from threading import Thread
from queue import Queue
from time import sleep
import pandas as pd

from src.modules import sti_module, plan_module, request_module
from gui.base import StatusGUI
from gui.log_handler import GuiLogHandler
from src.logs.logger import setup_logger


def worker():
    logger = logging.getLogger("tnb")

    while True:
        try:
            logger.info("🔄 Iniciando novo ciclo")

            sti_df = sti_module()
            logger.info("📥 Dados STI carregados")

            plan_df = plan_module()
            logger.info("📥 Dados PLAN carregados")

            logger.info("🔗 Realizando merge dos dados")
            df = pd.merge(sti_df, plan_df, on="Veiculo", how="outer")

            logger.info("📤 Iniciando envio dos dados")
            request_module(df)

            logger.info("⏳ Ciclo finalizado. Aguardando próximo ciclo...\n")
            sleep(10)

        except Exception as e:
            logger.exception("❌ Erro no ciclo")
            sleep(10)


if __name__ == "__main__":
    import logging

    gui_queue = Queue()

    logger, _, listener = setup_logger()

    gui_handler = GuiLogHandler(gui_queue)
    logger.addHandler(gui_handler)

    Thread(target=worker, daemon=True).start()

    app = StatusGUI(gui_queue)
    app.mainloop()

    listener.stop()
