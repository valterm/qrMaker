import lib.gui as gui
import lib.qrfactory as qr
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class App:
    def __init__(self):
        self.qrfactory = qr.QrFactory()
        self.ui = gui.Ui(self.qrfactory)

if __name__ == "__main__":
    logger.debug("start...")
    app = App()
    app.ui.start()
