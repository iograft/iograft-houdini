# Copyright 2022 Fabrica Software, LLC

import iograft
import iobasictypes

import hou
from ioghoudini_threading import houdini_main_thread


class HipFileClear(iograft.Node):
    """
    Clear the contents of the current scene file.
    """
    suppress_save_prompt = iograft.InputDefinition("suppress_save_prompt",
                                                   iobasictypes.Bool(),
                                                   default_value=False)

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("clear_hip_file")
        node.SetMenuPath("Houdini")
        node.AddInput(cls.suppress_save_prompt)
        return node

    @staticmethod
    def Create():
        return HipFileClear()

    @houdini_main_thread
    def Process(self, data):
        suppress_save_prompt = iograft.GetInput(self.suppress_save_prompt, data)

        # Clear the scene.
        hou.hipFile.clear(suppress_save_prompt=suppress_save_prompt)


def LoadPlugin(plugin):
    node = HipFileClear.GetDefinition()
    plugin.RegisterNode(node, HipFileClear.Create)
