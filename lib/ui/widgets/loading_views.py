import os

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QMovie, QPainter
from PyQt5.QtWidgets import QListView, QListWidget, QTableView, QTableWidget

LOADING_MOVIE = os.path.join(os.path.dirname(__file__), 'images', 'loading.gif')


class LoadingViewMixin:

    def __init__(self, parent=None, loading_text='Loading...',
                 loading_flags=Qt.AlignCenter, movie=LOADING_MOVIE):
        super().__init__(parent)
        self._movie = QMovie(movie)
        self._movie.setScaledSize(QSize(12, 12))
        self._movie.frameChanged.connect(self.viewport().update)

        self._loading = False
        self._loading_text = loading_text
        self._loading_flags = loading_flags
        self._scroll_policy = self.verticalScrollBarPolicy()

    def loading(self):
        return self._loading

    def setLoading(self, value):
        self._loading = bool(value)
        if self._loading:
            self.blockSignals(True)
            self._movie.start()
            super().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self._movie.stop()
            super().setVerticalScrollBarPolicy(self._scroll_policy)
            self.viewport().update()
            self.blockSignals(False)

    def setVerticalScrollBarPolicy(self, policy):
        self._scroll_policy = self.verticalScrollBarPolicy()
        super().setVerticalScrollBarPolicy(policy)

    def loadingText(self):
        return self._loading_text

    def setLoadingText(self, value):
        self._loading_text = value

    def paintEvent(self, event):
        # If loading flag is set, model is being populated, show a waiting animation
        if self._loading:
            painter = QPainter(self.viewport())
            pixmap = self._movie.currentPixmap()

            fm = self.fontMetrics()
            if self._loading_flags == Qt.AlignLeft:
                pix_pos = self.rect().translated(
                    self.width() / 2 - fm.width(self._loading_text) / 2 - pixmap.width() - 3,
                    self.height() / 2 - pixmap.height() / 2).topLeft()
                text_rect = self.rect()
            else:
                pix_pos = self.rect().translated(-pixmap.width() / 2, pixmap.height() / 2).center()
                text_rect = self.rect().translated(0, -fm.height() / 2)
            painter.drawPixmap(pix_pos, pixmap)
            painter.drawText(text_rect, Qt.AlignCenter, self._loading_text)

        # If model is empty, show a placeholder text
        elif self.model() is None or self.model().rowCount() == 0:
            painter = QPainter(self.viewport())

            painter.drawText(self.rect(), Qt.AlignCenter, 'No data')

        else:
            super().paintEvent(event)

    def keyPressEvent(self, event):
        # No keypress event allowed when loading flag is set
        if not self._loading:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        # No wheel event allowed when loading flag is set
        if not self._loading:
            super().wheelEvent(event)


class LoadingListView(LoadingViewMixin, QListView):
    pass


class LoadingListWidget(LoadingViewMixin, QListWidget):
    pass


class LoadingTableView(LoadingViewMixin, QTableView):
    pass


class LoadingTableWidget(LoadingViewMixin, QTableWidget):
    pass


if __name__ == "__main__":

    import sys
    import time
    import random

    from PyQt5.QtCore import QThread, pyqtSignal
    from PyQt5.QtGui import QStandardItemModel, QStandardItem

    random.seed()

    thread = None


    class Thread(QThread):

        itemReady = pyqtSignal(str)
        populateFinished = pyqtSignal()

        def __init__(self, parent=None):
            super().__init__(parent)
            self._should_stop = False

        def run(self):
            for i in range(15):
                if self._should_stop:
                    return

                self.itemReady.emit(f"Test {i+1}")
                time.sleep(random.uniform(0.1, 0.5))

            self.populateFinished.emit()

        def stop(self):
            self._should_stop = True


    def item_ready(text):
        item = QStandardItem(text)
        listview.setLoadingText(f'Loading {text}...')
        model.appendRow(item)


    def populate_finished():
        listview.setLoading(False)
        tableview.setLoading(False)


    def refresh_list():
        global thread
        if thread and thread.isRunning():
            thread.stop()

        listview.setLoading(True)
        tableview.setLoading(True)
        model.setRowCount(0)

        thread = Thread()
        thread.itemReady.connect(item_ready)
        thread.populateFinished.connect(populate_finished)
        thread.start()


    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    vlayout = QtWidgets.QVBoxLayout()
    hlayout = QtWidgets.QHBoxLayout()

    widget.setLayout(vlayout)
    listview = LoadingListView()
    tableview = LoadingTableView()
    hlayout.addWidget(listview)
    hlayout.addWidget(tableview)
    vlayout.addLayout(hlayout)

    button = QtWidgets.QPushButton('Refresh')
    vlayout.addWidget(button)
    button.clicked.connect(refresh_list)

    model = QStandardItemModel()

    listview.setModel(model)
    tableview.setModel(model)

    widget.show()

    sys.exit(app.exec_())

