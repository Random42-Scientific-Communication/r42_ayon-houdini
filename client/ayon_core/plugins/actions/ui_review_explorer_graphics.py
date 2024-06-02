from qtpy import QtWidgets, QtGui, QtCore
import os

class ReviewExplorerUIGraphics(QtWidgets.QDialog):
    """
    The Graphics part of the UI to get the reviews from
    """

    def __init__(self):
        super().__init__()

        # -- Set Window Properties
        self.setWindowTitle("Review_Explorer")
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setMinimumWidth(300)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setStyleSheet(load_stylesheet())

        # -- Create the layout
        self.layout = QtWidgets.QVBoxLayout()
        self.product_widget = QtWidgets.QWidget()
        self.product_layout= QtWidgets.QHBoxLayout(self.product_widget)

        self.layout = QtWidgets.QVBoxLayout()
        self.exr_widget = QtWidgets.QWidget()
        self.exr_layout = QtWidgets.QHBoxLayout(self.exr_widget)

        # -- Create the widgets
        self.labelProducts = QtWidgets.QLabel("Review Products")
        self.comboProducts = QtWidgets.QComboBox()
        self.buttonReview = QtWidgets.QPushButton("Open Selected Review Folder")
        self.buttonXDriveFolder = QtWidgets.QPushButton("Open X Drive Folder")
        self.buttonMoveToX = QtWidgets.QPushButton("Move Selected to X Drive")
        self.buttonLatestToX = QtWidgets.QPushButton("Move Latest to X Drive")

        self.labelEXRs = QtWidgets.QLabel("EXRs Products")
        self.comboEXRs = QtWidgets.QComboBox()
        self.buttonEXRs = QtWidgets.QPushButton("Open Selected EXRs Folder")

        self.checkDebug = QtWidgets.QCheckBox("Toggle_Debug")
        self.debugBox = QtWidgets.QPlainTextEdit()
        self.debugBox.setVisible(False)

        # -- Attaching widgets to layout
        self.product_layout.addWidget(self.labelProducts)
        self.product_layout.addWidget(self.comboProducts)

        self.exr_layout.addWidget(self.labelEXRs)
        self.exr_layout.addWidget(self.comboEXRs)

        self.layout.addWidget(self.product_widget)
        self.layout.addWidget(self.buttonReview)
        self.layout.addWidget(self.buttonXDriveFolder)
        self.layout.addWidget(self.buttonMoveToX)
        self.layout.addWidget(self.buttonLatestToX)
        self.layout.addWidget(self.exr_widget)
        self.layout.addWidget(self.buttonEXRs)
        self.layout.addWidget(self.checkDebug)
        self.layout.addWidget(self.debugBox)
        self.setLayout(self.layout)


def load_stylesheet():
    path = os.path.join(os.path.dirname(__file__), "action_menu_style.qss")
    if not os.path.exists(path):
        print("Unable to load stylesheet, file not found in resources")
        return ""

    with open(path, "r") as file_stream:
        stylesheet = file_stream.read()
    return stylesheet