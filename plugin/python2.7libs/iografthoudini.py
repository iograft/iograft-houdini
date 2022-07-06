# Copyright 2022 Fabrica Software, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess

import iograft
import hou

# The name of the Core object to be registered for the Houdini session.
IOGRAFT_HOUDINI_CORE_NAME = "houdini"


def start_iograft():
    """
    Start an iograft session for the current Houdini process. This creates a
    single Core object that can be shared/accessed throughout the current
    Houdini process.
    """
    if not iograft.IsInitialized():
        iograft.Initialize()

    # Ensure there is a "houdini" iograft Core object created and setup to
    # handle requests.
    core = iograft.GetCore(IOGRAFT_HOUDINI_CORE_NAME, True)

    # Ensure that the core's request handler is active so a UI can be
    # connected.
    core.StartRequestHandler()

    # Get the core address that clients (such as a UI) can connect to.
    core_address = core.GetClientAddress()
    hou.ui.displayMessage("iograft Core: '{}' running at: {}".format(
                            IOGRAFT_HOUDINI_CORE_NAME,
                            core_address))


def stop_iograft():
    """
    Shutdown the core object currently running inside of Houdini. If no Core
    is currently running, this functions takes no action.
    """
    if not iograft.IsInitialized():
        hou.ui.displayMessage("The iograft API is not currently initialized.",
                              severity=hou.severityType.Warning)
        return

    # Otherwise, clear the "houdini" Core object and uninitialize iograft.
    try:
        iograft.UnregisterCore(IOGRAFT_HOUDINI_CORE_NAME)
    except KeyError:
        pass

    # Uninitialize iograft.
    iograft.Uninitialize()
    hou.ui.displayMessage("The iograft API has been uninitialized.")


def launch_iograft_ui():
    """
    Launch an iograft UI session that can connect to the iograft Core
    object running inside of Houdini.
    """
    # Check that iograft is initialized.
    if not iograft.IsInitialized():
        hou.ui.displayMessage("The iograft API is not currently initialized.",
                              severity=hou.severityType.Warning)
        return

    # Try to get the "houdini" Core object.
    core_address = ""
    try:
        core = iograft.GetCore(IOGRAFT_HOUDINI_CORE_NAME,
                               create_if_needed=False)
        core_address = core.GetClientAddress()
    except KeyError:
        hou.ui.displayMessage(
                "No iograft Core: '{}' is currently running.".format(
                    IOGRAFT_HOUDINI_CORE_NAME),
                severity=hou.severityType.Error)
        return

    # Sanitize the environment for the iograft_ui session; removing the
    # LD_LIBRARY_PATH so we don't conflict with other Qt libraries and
    # clearing the IOGRAFT_ENV environment variable since the UI process
    # will no longer be running under the Houdini interpreter.
    subprocess_env = os.environ.copy()
    subprocess_env.pop("LD_LIBRARY_PATH", None)
    subprocess_env.pop("IOGRAFT_ENV", None)

    # Launch the iograft_ui subprocess.
    subprocess.Popen(["iograft_ui", "-c", core_address], env=subprocess_env)
