# -*- coding: utf-8 -*-
"""Collector plugin for frames data on ROP instances."""
import pyblish.api
from ayon_core.lib import (
    is_in_tests,
    BoolDef,
    NumberDef,
    EnumDef,
    TextDef
)
from ayon_core.pipeline.publish import AYONPyblishPluginMixin


class CollectR42PublishAttributes(pyblish.api.InstancePlugin,
                                     AYONPyblishPluginMixin):
    """We condense all the UI information here
    In this case, we could share parameters
    """

    # This specific order value is used so that
    # this plugin runs after CollectAnatomyInstanceData
    order = pyblish.api.CollectorOrder + 0.499
    label = "Collect R42 Publish Attributes"

    hosts = ['max']
    families = ["maxrender"]
    targets = ["local"]


    use_published = True
    use_preview_frames = False
    preview_priority = 50
    preview_frame_skip = 2
    preview_initial_status = "Active"
    priority = 50
    chunk_size = 1
    initial_status = "Active"
    group = None

    @classmethod
    def get_attribute_defs(cls):

        return [
            TextDef("group",
                    default=cls.group,
                    label="Group Name"),
            BoolDef("use_published",
                    default=cls.use_published,
                    label="Use Published Scene"),
            NumberDef(
                "chunk_size",
                label="Frames Per Task",
                default=cls.chunk_size,
                decimals=0,
                minimum=1,
                maximum=1000
            ),
            BoolDef(
                "use_preview_frames",
                default=cls.use_preview_frames,
                label="Use Preview Frames"
            ),
            NumberDef(
                "preview_priority",
                label="Preview Priority",
                default=cls.preview_priority,
                decimals=0
            ),
            NumberDef(
                "preview_frame_skip",
                label="Preview Frame Skip",
                default=cls.preview_frame_skip,
                decimals=0
            ),
            NumberDef(
                "priority",
                label="Priority",
                default=cls.priority,
                decimals=0
            ),
            EnumDef("preview_initial_status",
                    label="Preview Render Initial Status",
                    items=["Active", "Suspended"],
                    default=cls.preview_initial_status),
            EnumDef("initial_status",
                    label="Render Initial Status",
                    items=["Active", "Suspended"],
                    default=cls.initial_status)
        ]


    def process(self, instance):
        attr_values = self.get_attr_values_from_data(instance.data)
        self.log.info(f"use_published : {attr_values.get('use_published', self.use_published)}")
        self.log.info(f"group : {attr_values.get('group', self.group)}")
        self.log.info(f"use_preview_frames : {attr_values.get('use_preview_frames', self.use_preview_frames)}")
        self.log.info(f"preview_priority : {attr_values.get('preview_priority', self.preview_priority)}")
        self.log.info(f"preview_frame_skip : {attr_values.get('preview_frame_skip', self.preview_frame_skip)}")
        self.log.info(f"preview_initial_status : {attr_values.get('preview_initial_status', self.preview_initial_status)}")
        self.log.info(f"priority : {attr_values.get('priority', self.priority)}")
        self.log.info(f"chunk_size : {attr_values.get('chunk_size', self.chunk_size)}")
        self.log.info(f"initial_status : {attr_values.get('initial_status', self.initial_status)}")

        # Store all attributes
        instance.data["use_published"] = attr_values.get('use_published', self.use_published)
        instance.data["group"] = attr_values.get('group', self.group)
        instance.data["use_preview_frames"] = attr_values.get('use_preview_frames', self.use_preview_frames)
        instance.data["preview_priority"] = attr_values.get('preview_priority', self.preview_priority)
        instance.data["preview_frame_skip"] = attr_values.get('preview_frame_skip', self.preview_frame_skip)
        instance.data["preview_initial_status"] = attr_values.get('preview_initial_status', self.preview_initial_status)
        instance.data["priority"] = attr_values.get('priority', self.priority)
        instance.data["chunk_size"] = attr_values.get('chunk_size', self.chunk_size)
        instance.data["initial_status"] = attr_values.get('initial_status', self.initial_status)

        # Store helper attributes
        instance.data["previewDeadlineSubmissionJob"] = None

    @classmethod
    def apply_settings(cls, project_settings):
        settings = project_settings["deadline"]["publish"]["MaxSubmitDeadline"]  # noqa
        cls.group = settings.get("group", cls.group)


