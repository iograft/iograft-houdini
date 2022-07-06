# iograft for Houdini

This repository contains scripts and nodes for running iograft within Houdini. It includes a subcore command for executing Houdini in batch from iograft, a plugin for using iograft interactively in Houdini, and a few example iograft Houdini nodes.

## Getting started with a Houdini environment

Below are the steps required to setup a new environment in iograft for executing nodes in Houdini.

1. Clone this iograft-houdini repository.
2. Open the iograft Environment Manager and create a new environment for Houdini (i.e. "houdini19").
3. Add the "nodes" directory of the iograft-houdini repository to the **Plugin Path**.
4. Update the **Subcore Launch Command** to the `ioghoudini_subcore` command. Note: On Windows this will automatically resolve to the `ioghoudini_subcore.bat` script.
5. Add the "bin" directory of the iograft-houdini repository to the **Path**.
6. Add the directory containing the Houdini and hython executables to the **Path**.
7. Add the "python" directory of the iograft-houdini repository to the **Python Path**.
8. Depending on the version of Houdini, update the **Python Path** entry for `...\iograft\python39` by switching "python39" to the directory for the correct version of Python (for Houdini 19, this is "python37").

<details><summary>Example Houdini environment JSON</summary>
<p>

```json
{
    "plugin_path": [
        "C:\\Program Files\\iograft\\types",
        "C:\\Program Files\\iograft\\nodes",
        "{IOGRAFT_USER_CONFIG_DIR}\\types",
        "{IOGRAFT_USER_CONFIG_DIR}\\nodes",
        "C:\\Users\\dtkno\\Projects\\iograft-public\\iograft-houdini\\nodes"
    ],
    "subcore": {
        "launch_command": "ioghoudini_subcore"
    },
    "path": [
        "C:\\Program Files\\iograft\\bin",
        "C:\\Program Files\\Side Effects Software\\Houdini 19.0.531\\bin",
        "C:\\Users\\dtkno\\Projects\\iograft-public\\iograft-houdini\\bin"
    ],
    "python_path": [
        "C:\\Program Files\\iograft\\types",
        "C:\\Program Files\\iograft\\python37",
        "C:\\Users\\dtkno\\Projects\\iograft-public\\iograft-houdini\\python"
    ],
    "environment_variables": {},
    "appended_environments": [],
    "name": "houdini19"
}
```

</p>
</details>


## Using iograft within Houdini

To use iograft within a Houdini interactive session, we need to ensure the iograft libraries are accessible to Houdini (via the Path/Python Path), and tell iograft what environment we are in. These steps can either be done using the iograft Plugin for Houdini, or by launching Houdini using `iograft_env`.

### iograft Plugin for Houdini

This is the easiest method to begin using iograft within Houdini. The "plugin" directory of this repository contains an `iografthoudini.json` package definition containing information for initializing iograft's Houdini plugin.

To install the iograft package, simply create a "packages" subdirectory inside your Houdini preferences directory (i.e. C:/Users/dtkno/Documents/houdini19.0/packages) and place the `iografthoudini.json` file from this repository into that package folder. For help on where to copy this package JSON, see the [Houdini Docs](https://www.sidefx.com/docs/houdini/ref/plugins.html).

Then you will need to edit the `iografthoudini.json` file to point to your specific iograft locations and houdini environment name.
- `IOGRAFT_HOUDINI` should point to the "plugin" directory of this repository.
- `IOGRAFT_HOUDINI_ENV` should be the name of the iograft environment created for Houdini.
- `PYTHONPATH` should be updated to either the python37 or python27 directory of the iograft installation based on which version of Houdini you are using.

```json
{
    "env": [
        {
            "IOGRAFT_HOUDINI": "C:/Users/dtkno/Projects/iograft-public/iograft-houdini/plugin"            
        },
        {
            "IOGRAFT_HOUDINI_ENV": "houdini19"
        },
        {
            "PYTHONPATH": {
                "value": "C:/Program Files/iograft/python37",
                "method": "append"
            }
        }
    ],
    "path": "$IOGRAFT_HOUDINI"
}
```

Once updated, verify that the package is loading properly by using the "+" button next to the Shelf menu and toggling on the shelf named "iograft".

### iograft Shelf Tools

The plugin creates an iograft Shelf and registers 3 operations:

1. **Start** -
Used to initialize a local iograft session within Houdini. Starts an iograft Core using the builtin Houdini Python interpreter. A UI session can be connected to this iograft Core for graph authoring and monitoring.

2. **Stop** -
Used to shutdown the iograft session within Houdini.

3. **Launch UI** -
Launch the iograft UI as a subprocess and connect to the iograft Core running inside of Houdini. Note: The UI runs in a completely separate process and not internally in Houdini. Only the iograft Core runs inside of Houdini.

All other operations for interacting with the Core object should be completed using the iograft Python API.

When the **Start** operation is executed, it registers a Core named "houdini" that can be retrieved with the Python API as shown below:

```python
import iograft
core = iograft.GetCore("houdini")
```

Using the Python API, we have access to useful functionality on the Core such as loading graphs, setting input values on a graph, and processing the graph.


### iograft_env

The second method for launching Houdini so iograft can be used is via `iograft_env`. iograft_env first initializes all of the environment variables contained within the environment JSON and then launches the given command (`houdini` in the example below).

```bat
iograft_env -e houdini19 -c houdini
```

Note: Using this method to use iograft within an interactive Houdini session will not create the iograft Shelf, but will only setup the necessary environment to use the iograft API.


## Threading in Houdini

Some of the available Houdini Python commands are expected to be run in the main thread (or else there is the possibility for errors and undefined behavior). To get around any threading issues, there are a couple of additions we can make to the Houdini scripts and nodes.

1. Nodes that execute Houdini commands that may be unsafe in a threaded environment must apply the `@houdini_main_thread` decorator to their `Process` function. When running iograft interactively in Houdini, this decorator makes use of Houdini's `hdefereval.executeInMainThreadWithResult` function to process the node in Houdini's main thread.

2. To avoid blocking the main thread when processing graphs in an interactive Houdini session, processing must be started with either the `StartGraphProcessing()` function which is non-blocking, or pass the `execute_in_main_thread` argument to `ProcessGraph(execute_in_main_thread=True)` to ensure that nodes that require the main thread can be completed successfully.

3. When processing Houdini nodes in batch (i.e. when using the Houdini Subcore), `ioghoudinipy_subcore.py` executes all nodes in the main thread. To do this, it makes use of the `iograft.MainThreadSubcore` class which runs the primary `iograft.Subcore.ListenForWork` listener in a secondary thread while processing nodes in the main thread.
