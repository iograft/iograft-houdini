# Copyright 2022 Fabrica Software, LLC

import iograft
import iobasictypes

import hou
from ioghoudini_threading import houdini_main_thread


class HipFileSave(iograft.Node):
    """
    Save the current scene to a .hip file.
    """
    filename = iograft.InputDefinition("filename", iobasictypes.Path())
    save_to_recent_files = iograft.InputDefinition("save_to_recent_files",
                                                   iobasictypes.Bool(),
                                                   default_value=False)
    out_filename = iograft.OutputDefinition("out_filename", iobasictypes.Path())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("save_hip_file")
        node.AddInput(cls.filename)
        node.AddInput(cls.save_to_recent_files)
        node.AddOutput(cls.out_filename)
        return node

    @staticmethod
    def Create():
        return HipFileSave()

    @houdini_main_thread
    def Process(self, data):
        filename = iograft.GetInput(self.filename, data)
        save_to_recent_files = iograft.GetInput(self.save_to_recent_files, data)

        # Save the scene.
        hou.hipFile.save(file_name=filename,
                         save_to_recent_files=save_to_recent_files)

        # Return the filepath that the scene was saved to.
        out_filename = hou.hipFile.path()
        iograft.SetOutput(self.out_filename, data, out_filename)


def LoadPlugin(plugin):
    node = HipFileSave.GetDefinition()
    plugin.RegisterNode(node, HipFileSave.Create)
