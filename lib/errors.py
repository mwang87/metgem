import os
import sys
import traceback
import logging

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMessageBox, qApp


class UserRequestedStopError(Exception):
    """Raised if user request to stop a worker's process"""


class UnsupportedVersionError(OSError):
    pass


# noinspection PyArgumentList
def exceptionHandler(exctype, value, trace):
    """
        This exception handler prevents quitting to the command line when there is
        an unhandled exception while processing a Qt signal.

        The script/application willing to use it should implement code similar to:

        .. code-block:: python

            if __name__ == "__main__":
                sys.excepthook = exceptionHandler

        """

    if exctype == KeyboardInterrupt:
        sys.__excepthook__(exctype, value, trace)
        sys.exit()

    if trace is not None:
        msg = f"{exctype.__name__} in {trace.tb_frame.f_code.co_name}"
    else:
        msg = exctype.__name__
    logger = logging.getLogger()
    logger.error(msg, exc_info=(exctype, value, trace))
    msg = QMessageBox(qApp.activeWindow())
    msg.setWindowTitle("Unhandled exception")
    msg.setIcon(QMessageBox.Warning)
    msg.setText(("It seems you have found a bug in {}. Please report details.\n"
                 "You should restart the application now.").format(QCoreApplication.applicationName()))
    msg.setInformativeText(str(value))
    msg.setDetailedText(''.join(traceback.format_exception(exctype, value, trace)))
    btRestart = msg.addButton("Restart now", QMessageBox.ResetRole)
    msg.addButton(QMessageBox.Ignore)
    msg.raise_()
    msg.exec_()
    if msg.clickedButton() == btRestart:  # Restart application
        os.execv(sys.executable, [sys.executable] + sys.argv)