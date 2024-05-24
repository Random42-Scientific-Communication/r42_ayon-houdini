import os
from ayon_core.pipeline import (
    Anatomy,
    LauncherAction,
)
from ayon_core import resources

from ayon_core.plugins.actions import ui_review_explorer
from qtpy import QtCore, QtWidgets

import importlib
importlib.reload(ui_review_explorer)


class PublishDetectionAction(LauncherAction):
    name = "publish_explorer"
    label = "Publish Explorer"
    icons = resources.get_resource("icons")
    icon = os.path.join(icons, "circle_yellow.png")
    order = 500

    def __init__(self):
        super(PublishDetectionAction, self).__init__()

    def is_compatible(self, selection):
        """Return whether the action is compatible with the session"""
        return selection.is_folder_selected

    def process(self, session, **kwargs):
        app = QtWidgets.QApplication.instance()
        window = ui_review_explorer.ReviewExplorerUI(session)
        window.exec_()
