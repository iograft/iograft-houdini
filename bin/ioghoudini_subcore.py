#!/usr/bin/env python
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

import argparse
import os
import sys

import iograft


def parse_args():
    parser = argparse.ArgumentParser(
                description="Start an iograft subcore to process in Houdini")
    parser.add_argument("--core-address", dest="core_address", required=True)
    return parser.parse_args()


def EnableHouModule():
    """
    If not launching the subcore with 'hython' (i.e. running the Subcore
    through a different Python interpreter), this must be used to enable the
    houdini libraries in the current Python interpreter. This is handled
    automatically if using the 'hython' command.
    """
    # Importing hou will load Houdini's libraries and initialize Houdini.
    # This will cause Houdini to load any HDK extensions written in C++.
    # These extensions need to link against Houdini's libraries,
    # so the symbols from Houdini's libraries must be visible to other
    # libraries that Houdini loads. To make the symbols visible, we add the
    # RTLD_GLOBAL dlopen flag.
    if hasattr(sys, "setdlopenflags"):
        old_dlopen_flags = sys.getdlopenflags()
        sys.setdlopenflags(old_dlopen_flags | os.RTLD_GLOBAL)

    try:
        import hou
    finally:
        # Reset dlopen flags back to their original value.
        if hasattr(sys, "setdlopenflags"):
            sys.setdlopenflags(old_dlopen_flags)


def StartSubcore(core_address):
    # Ensure that the 'hou' module can be loaded.
    EnableHouModule()

    # Initialize iograft.
    iograft.Initialize()

    # Create the Subcore object and listen for nodes to be processed. Use
    # the MainThreadSubcore to ensure that all nodes are executed in the
    # main thread.
    subcore = iograft.MainThreadSubcore(core_address)
    subcore.ListenForWork()

    # Uninitialize iograft.
    iograft.Uninitialize()


if __name__ == "__main__":
    args = parse_args()

    # Start the subcore.
    StartSubcore(args.core_address)
