import os
import platform
import subprocess
import importlib
import shutil
from datetime import datetime
from ayon_core.plugins.actions import ui_review_explorer_graphics
from ayon_core.pipeline import Anatomy
from ayon_core.pipeline.template_data import get_template_data
from qtpy import QtWidgets, QtGui, QtCore

import pprint
import ayon_api
importlib.reload(ui_review_explorer_graphics)


class DataInstance:
    def __init__(self, data):
        self.name = data["subset_name"]
        self.path = data["rep_path"]
        self.directory = os.path.dirname(self.path)
        self.project_name = data["project_name"]
        self.project_code = data["project_code"]
        self.shot_name = data["shot_name"]
        self.folder_path = data["folder_path"]
        self.rep_created = data["rep_created"]


class ReviewExplorerUI(ui_review_explorer_graphics.ReviewExplorerUIGraphics):
    """
    The Logic of the UI to clean up renders
    """

    def __init__(self, selection):
        super(ReviewExplorerUI, self).__init__()
        # -- Data
        self.selection = selection
        self.project_name = None
        self.folder_name = self.folder_id = self.folder_path = None
        self.x_dir = self.x_file = None
        self.review_instance_dict = {}

        self._populate_data()
        self.debug()

        # -- Connect
        self.connect_ui()
        self.populate_review_instances()

    # ------------------------
    # -- UI FUNCTIONS --
    # ------------------------
    def connect_ui(self):
        self.buttonReview.clicked.connect(self.open_review_dir)
        self.buttonXDriveFolder.clicked.connect(self.open_x_drive_path)
        self.buttonMoveToX.clicked.connect(self.copy_selected_to_x)
        self.buttonLatestToX.clicked.connect(self.copy_latest_to_x)
        self.checkDebug.stateChanged.connect(self.debug_visibility)

    def debug_visibility(self):
        self.debugBox.setVisible(self.checkDebug.isChecked())
        self.adjustSize()

    def _populate_data(self):
        self.project_name = self.selection.project_name
        self.folder_id = self.selection.folder_id

        folder_entity = self.selection.folder_entity
        self.folder_name = folder_entity["name"]
        self.folder_path = folder_entity["path"]

        self.populate_prores_data()
        self.populate_x_drive_path()

    def _check_valid_representation(self, rep_data):
        # ---- Check if it is ProRes representation ----
        '''
        0 - Not Valid
        1 - Review
        2- Exrs
        '''
        try:
            if rep_data["context"]["output"] != "ProRes":
                return 0
        except KeyError:
            return 0

        # ---- Check if it is storyboard comp ----
        task_type = rep_data["context"]["task"]["type"]
        if task_type == "Storyboard Comp":
            return 0

        # ---- Check if the folder is shot context ----
        shot_name = rep_data["context"]["folder"]["name"]
        folder_data = ayon_api.get_folder_by_name(project_name=self.project_name,
                                                  folder_name=shot_name)
        if folder_data["folderType"] != "Shot":
            return 0

        return 1

    def populate_prores_data(self):
        # ---- Query the products ----
        product_list = ayon_api.get_products(project_name=self.project_name,
                                             folder_ids=[self.folder_id],
                                             product_types=["review", "render"],
                                             )
        product_list = list(product_list)

        # ---- Query the versions ----
        version_list = []
        for product in product_list:
            product_id = product["id"]
            version_data = ayon_api.get_hero_version_by_product_id(project_name=self.project_name,
                                                                   product_id=product_id,
                                                                   )
            version_list.append(version_data)

        # ---- Query the representation ----
        for version in version_list:
            try:
                representation_data = ayon_api.get_representations(project_name=self.project_name,
                                                                   version_ids=[version['id']])
                rep_data_as_list = list(representation_data)
                for rep in rep_data_as_list:
                    valid = self._check_valid_representation(rep)
                    if valid == 0:
                        continue

                    file_path = rep['attrib']['path']
                    modified_time = os.path.getmtime(file_path)
                    modified_time_format = datetime.fromtimestamp(modified_time).isoformat()

                    # ---- Extract out the essential data ----
                    data = {
                        "subset_name": rep["context"]["subset"],
                        "rep_path": rep['attrib']['path'],
                        "project_name": self.project_name,
                        "project_code": rep["context"]["project"]["code"],
                        "shot_name": rep["context"]["folder"]["name"],
                        "folder_path": self.folder_path,
                        "rep_created": modified_time_format
                    }
                    data_instance = DataInstance(data)
                    self.review_instance_dict[data['subset_name']] = data_instance

            except TypeError:
                continue

    def populate_x_drive_path(self):
        anatomy = Anatomy(
            self.project_name,
            project_entity=self.selection.project_entity
        )
        data = get_template_data(
            self.selection.project_entity,
            self.selection.folder_entity,
            self.selection.task_entity
        )
        data["ext"] = "mov"

        x_dir = anatomy.get_template_item(
            "publish", "video", "folder"
        ).format(data)
        self.x_dir = os.path.normpath(x_dir)
        self.x_file = anatomy.get_template_item(
            "publish", "video", "file"
        ).format(data)

    def populate_review_instances(self):
        self.comboProducts.clear()
        for review_name in list(self.review_instance_dict.keys()):
            self.comboProducts.addItem(review_name)

    def compare_prores_data(self):
        latest_instance = None
        for key in self.review_instance_dict:
            instance = self.review_instance_dict[key]
            if not latest_instance:
                latest_instance = instance
                continue

            current_time = instance.rep_created
            latest_time = latest_instance.rep_created

            # Parse the datetime strings into datetime objects
            datetime_obj1 = datetime.fromisoformat(current_time)
            datetime_obj2 = datetime.fromisoformat(latest_time)

            # Compare the datetime objects
            if datetime_obj1 > datetime_obj2:
                latest_instance = instance
            else:
                continue

        return latest_instance

    def open_x_drive_path(self):
        x_drive_path = self.x_dir
        if not os.path.exists(x_drive_path):
            os.makedirs(x_drive_path)
        self.open_in_explorer(x_drive_path)

    def open_review_dir(self):
        product_name = self.comboProducts.currentText()
        path = self.review_instance_dict[product_name].directory
        if not path:
            return

        self.open_in_explorer(path)

    def copy_to_x(self, old_path):
        new_path = os.path.join(self.x_dir, self.x_file)
        old_path = os.path.normpath(old_path)
        new_path = os.path.normpath(new_path)
        try:
            shutil.copy(old_path, new_path)
            QtWidgets.QMessageBox.information(self, "Copy Video",
                                              "Complete")
        except PermissionError:
            QtWidgets.QMessageBox.information(self, "Copy Video",
                                              "PermissionError: File might be opened in another location")

    def copy_selected_to_x(self):
        product_name = self.comboProducts.currentText()
        old_path = self.review_instance_dict[product_name].path
        self.copy_to_x(old_path)

    def copy_latest_to_x(self):
        latest_instance = self.compare_prores_data()
        old_path = latest_instance.path
        self.copy_to_x(old_path)

    def debug(self):
        message = ""
        message += f"self.folder_path: {self.folder_path}\n"
        message += f"\n**************************\n"

        for key in self.review_instance_dict:
            instance = self.review_instance_dict[key]
            message_dict = pprint.pformat(instance.__dict__)
            message += message_dict
            message += f"\n**************************\n"

        message += f"\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
        try:
            latest_instance = self.compare_prores_data()
            message_dict = pprint.pformat(latest_instance.__dict__)
            message += message_dict
        except AttributeError:
            message += "NO PRORES DATA FILE YET"
        message += f"\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"


        message += f"\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
        message += f"video_dir: {self.x_dir}\n"
        message += f"video_file: {self.x_file}"
        message += f"\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"

        self.debugBox.setPlainText(message)

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