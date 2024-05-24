import os
import platform
import subprocess
from qtpy import QtWidgets, QtGui, QtCore
from string import Formatter
from ayon_core.pipeline import (
    Anatomy
)
from ayon_core.pipeline.template_data import get_template_data


class ReviewExplorerUI(QtWidgets.QDialog):
    """
    The UI to clean up renders
    """

    def __init__(self, selection):
        super(ReviewExplorerUI, self).__init__()
        self.selection = selection
        # -- Set Window Properties
        self.setWindowTitle("Review_Explorer")
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setMinimumWidth(300)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # -- Create the layout
        self.layout = QtWidgets.QVBoxLayout()

        # -- Create the widgets
        self.buttonReview = QtWidgets.QPushButton("Open Review Folder")
        self.buttonMoveToX = QtWidgets.QPushButton("Move reviews to X Drive")
        self.checkDebug = QtWidgets.QCheckBox("Toggle_Debug")
        self.debugBox = QtWidgets.QPlainTextEdit()
        self.debugBox.setVisible(True)

        # -- Attaching widgets to layout
        self.layout.addWidget(self.buttonReview)
        self.layout.addWidget(self.buttonMoveToX)
        self.layout.addWidget(self.checkDebug)
        self.layout.addWidget(self.debugBox)
        self.setLayout(self.layout)

        # -- Connect
        self.connect_ui()

    # ------------------------
    # -- UI FUNCTIONS --
    # ------------------------
    def connect_ui(self):
        self.buttonReview.clicked.connect(self.open_review_dir)
        self.buttonMoveToX.clicked.connect(self.debug)

    def debug(self):
        import pprint
        project_entity = pprint.pformat(self.selection.project_entity)
        folder_entity = pprint.pformat(self.selection.folder_entity)
        task_entity = pprint.pformat(self.selection.task_entity)
        message = f"project name is: {self.selection.project_name}\n" \
                  f"folder id is: {self.selection.folder_id}\n" \
                  f"folder_path: {self.selection.folder_path}\n" \
                  f"task id is: {self.selection.task_id}\n" \
                  f"task_name: {self.selection.task_name}\n" \
                  f"---------------------------------\n"
        message += f"project_entity: \n"
        message += project_entity
        message += f"\n---------------------------------\n"
        message += f"folder_entity: \n"
        message += folder_entity
        message += f"\n---------------------------------\n"
        message += f"task_entity: \n"
        message += task_entity
        message += f"\n---------------------------------\n"

        self.debugBox.setPlainText(message)

    def open_review_dir(self):
        path = self._get_hero_review_dir()
        if not path:
            return

        self.open_in_explorer(path)

    def _find_first_filled_path(self, path):
        if not path:
            return ""

        fields = set()
        for item in Formatter().parse(path):
            _, field_name, format_spec, conversion = item
            if not field_name:
                continue
            conversion = "!{}".format(conversion) if conversion else ""
            format_spec = ":{}".format(format_spec) if format_spec else ""
            orig_key = "{{{}{}{}}}".format(
                field_name, conversion, format_spec)
            fields.add(orig_key)

        for field in fields:
            path = path.split(field, 1)[0]
        return path

    def _get_hero_review_dir(self):
        data = get_template_data(
            self.selection.project_entity,
            self.selection.folder_entity,
            self.selection.task_entity
        )

        anatomy = Anatomy(
            self.selection.project_name,
            project_entity=self.selection.project_entity
        )
        review_dir = anatomy.get_template_item(
            "hero", "hero_review", "folder"
        ).format(data)

        # Remove any potential un-formatted parts of the path
        valid_review_dir = self._find_first_filled_path(review_dir)

        # Path is not filled at all
        if not valid_review_dir:
            raise AssertionError("Failed to calculate review directory.")

        # Normalize
        valid_review_dir = os.path.normpath(valid_review_dir)
        if os.path.exists(valid_review_dir):
            return valid_review_dir

        data.pop("task", None)
        review_dir = anatomy.get_template_item(
            "hero", "hero_review", "folder"
        ).format(data)
        valid_review_dir = self._find_first_filled_path(review_dir)
        if valid_review_dir:
            # Normalize
            valid_review_dir = os.path.normpath(valid_review_dir)
            if os.path.exists(valid_review_dir):
                return valid_review_dir
        raise AssertionError("Folder does not exist yet.")

    @staticmethod
    def open_in_explorer(path):
        platform_name = platform.system().lower()
        if platform_name == "windows":
            args = ["start", path]
        elif platform_name == "darwin":
            args = ["open", "-na", path]
        elif platform_name == "linux":
            args = ["xdg-open", path]
        else:
            raise RuntimeError(f"Unknown platform {platform.system()}")
        # Make sure path is converted correctly for 'os.system'
        os.system(subprocess.list2cmdline(args))