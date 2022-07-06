import atexit
import os
import iograft
import iografthoudini

# Initialize the iograft environment for houdini if it is defined.
if "IOGRAFT_HOUDINI_ENV" in os.environ:
    try:
        iograft.InitializeEnvironment(os.environ["IOGRAFT_HOUDINI_ENV"])
    except KeyError as e:
        print("Failed to initialize iograft environment: {}: {}".format(
                os.environ["IOGRAFT_HOUDINI_ENV"], e))


# Function to be used with atexit to ensure that iograft has been cleaned
# up and doesn't prevent Houdini from exiting.
@atexit.register
def _ensureUninitialized():
    # Ensure that the houdini Core is deleted.
    try:
        iograft.UnregisterCore(iografthoudini.IOGRAFT_HOUDINI_CORE_NAME)
    except KeyError:
        pass

    # Ensure iograft is uninitialized.
    if iograft.IsInitialized():
        iograft.Uninitialize()
