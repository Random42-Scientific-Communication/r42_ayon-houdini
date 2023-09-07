# -*- coding: utf-8 -*-
from maya import cmds  # noqa
import pyblish.api


class CollectRigFbx(pyblish.api.InstancePlugin):
    """Collect Unreal Skeletal Mesh."""

    order = pyblish.api.CollectorOrder + 0.2
    label = "Collect rig for fbx"
    families = ["rig"]

    def process(self, instance):
        if not instance.data.get("fbx_enabled"):
            self.log.debug("Skipping collecting rig data for fbx..")
            return

        frame = cmds.currentTime(query=True)
        instance.data["frameStart"] = frame
        instance.data["frameEnd"] = frame
        skeleton_sets = [
            i for i in instance[:]
            if i.lower().endswith("skeleton_set")
        ]

        skeleton_mesh_sets = [
            i for i in instance[:]
            if i.lower().endswith("skeletonmesh_set")
        ]
        if skeleton_sets or skeleton_mesh_sets:
            instance.data["families"] += ["fbx"]
            instance.data["geometries"] = []
            instance.data["control_rigs"] = []
            instance.data["skeleton_mesh"] = []
            for skeleton_set in skeleton_sets:
                skeleton_content = cmds.ls(
                    cmds.sets(skeleton_set, query=True), long=True)
                if skeleton_content:
                    instance.data["control_rigs"] += skeleton_content

            for skeleton_mesh_set in skeleton_mesh_sets:
                skeleton_mesh_content = cmds.ls(
                    cmds.sets(skeleton_mesh_set, query=True), long=True)
                if skeleton_mesh_content:
                    instance.data["skeleton_mesh"] += skeleton_mesh_content
