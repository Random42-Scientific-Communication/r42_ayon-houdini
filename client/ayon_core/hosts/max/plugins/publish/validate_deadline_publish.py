import os
import re
import pyblish.api
from pymxs import runtime as rt
from ayon_core.pipeline.publish import (
    RepairAction,
    ValidateContentsOrder,
    PublishValidationError,
    OptionalPyblishPluginMixin
)
from ayon_core.hosts.max.api.lib_rendersettings import RenderSettings
from ayon_core.settings import get_project_settings
from ayon_core.pipeline import get_current_project_name
from ayon_core.hosts.max.api.lib import (
    get_default_render_folder
)


class ValidateDeadlinePublish(pyblish.api.InstancePlugin,
                              OptionalPyblishPluginMixin):
    """Validates Render File Directory is
    not the same in every submission
    """

    order = ValidateContentsOrder
    families = ["maxrender"]
    hosts = ["max"]
    label = "Render Output for Deadline"
    optional = True
    actions = [RepairAction]

    def process(self, instance):
        if not self.is_active(instance.data):
            return
        expected_output_path = self.generate_temp_output_path()
        '''
        file = rt.maxFileName
        filename, ext = os.path.splitext(file)
        self.generate_temp_output_path()
        if filename not in rt.rendOutputFilename:
            raise PublishValidationError(
                "Render output folder "
                "doesn't match the max scene name! "
                "Use Repair action to "
                "fix the folder file path.."
            )
        '''
        if expected_output_path not in rt.rendOutputFilename:
            raise PublishValidationError(
                "Render output folder "
                "doesn't match the max scene name! "
                "Use Repair action to "
                "fix the folder file path.."
            )

    @classmethod
    def repair(cls, instance):
        container = instance.data.get("instance_node")
        RenderSettings().render_output(container)
        cls.log.debug("Reset the render output folder...")

    def generate_temp_output_path(self):
        folder = rt.maxFilePath

        folder = folder.replace("\\", "/")
        setting = get_project_settings(get_current_project_name())
        render_folder = get_default_render_folder(setting)

        ''' We remove the versioning in the temp files'''
        file = rt.maxFileName
        filename, ext = os.path.splitext(file)
        pattern = r"_v\d.*"
        filename = re.sub(pattern, "", filename)

        output_dir = os.path.join(folder,
                                  render_folder,
                                  filename)

        output_dir = os.path.normpath(output_dir)
        output_dir += "\\"

        self.log.debug(f"output_dir is {output_dir}")
        return output_dir
