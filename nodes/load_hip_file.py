# Copyright 2022 Fabrica Software, LLC

import iograft
import iobasictypes

import hou
from ioghoudini_threading import houdini_main_thread


class HipFileLoad(iograft.Node):
    """
    Load a scene (.hip) file.
    """
    filename = iograft.InputDefinition("filename", iobasictypes.Path())
    suppress_save_prompt = iograft.InputDefinition("suppress_save_prompt",
                                                   iobasictypes.Bool(),
                                                   default_value=False)
    ignore_load_warnings = iograft.InputDefinition("ignore_load_warnings",
                                                   iobasictypes.Bool(),
                                                   default_value=False)
    out_filename = iograft.OutputDefinition("filename", iobasictypes.Path())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("load_hip_file")
        node.SetMenuPath("Houdini")
        node.AddInput(cls.filename)
        node.AddInput(cls.suppress_save_prompt)
        node.AddInput(cls.ignore_load_warnings)
        node.AddOutput(cls.out_filename)
        return node

    @staticmethod
    def Create():
        return HipFileLoad()

    @houdini_main_thread
    def Process(self, data):
        filename = iograft.GetInput(self.filename, data)
        suppress_save_prompt = iograft.GetInput(self.suppress_save_prompt, data)
        ignore_load_warnings = iograft.GetInput(self.ignore_load_warnings, data)

        # Try the load operation.
        hou.hipFile.load(filename,
                         suppress_save_prompt=suppress_save_prompt,
                         ignore_load_warnings=ignore_load_warnings)

        # Pass the file name back to iograft.
        out_filename = hou.hipFile.path()
        iograft.SetOutput(self.out_filename, data, out_filename)


def LoadPlugin(plugin):
    node = HipFileLoad.GetDefinition()
    plugin.RegisterNode(node, HipFileLoad.Create)
