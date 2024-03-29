import pyblish.api

from ayon_core.lib import version_up
from ayon_core.pipeline import registered_host
from ayon_core.pipeline.publish import get_errored_plugins_from_context

from ayon_core.pipeline.publish import KnownPublishError


class IncrementCurrentFile(pyblish.api.ContextPlugin):
    """Increment the current file.

    Saves the current scene with an increased version number.

    """

    label = "Increment current file"
    order = pyblish.api.IntegratorOrder + 9.0
    hosts = ["houdini"]
    families = ["workfile",
                "redshift_rop",
                "arnold_rop",
                "usdrender",
                "render.farm.hou",
                "render.local.hou",
                "publish.hou"]
    optional = True

    def process(self, context):

        errored_plugins = get_errored_plugins_from_context(context)
        if any(
            plugin.__name__ == "HoudiniSubmitPublishDeadline"
            for plugin in errored_plugins
        ):
            raise KnownPublishError(
                "Skipping incrementing current file because "
                "submission to deadline failed."
            )

        # Filename must not have changed since collecting
        host = registered_host()  # type: HoudiniHost
        current_file = host.current_file()
        if context.data["currentFile"] != current_file:
            raise KnownPublishError(
                "Collected filename mismatches from current scene name."
            )

        new_filepath = version_up(current_file)
        host.save_workfile(new_filepath)
