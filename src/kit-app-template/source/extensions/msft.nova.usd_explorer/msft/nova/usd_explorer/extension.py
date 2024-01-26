# Copyright 2019-2023 NVIDIA CORPORATION

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import omni.ext
import omni.ui as ui
import os
import carb.imgui as _imgui
import carb.settings
import carb.tokens
import omni.kit.app
from pathlib import Path


from dotenv import load_dotenv

env = f"{Path(__file__).parents[5]}\\.env"

print(f"Looking for env file at {env}")

load_dotenv(env)

host = os.getenv('omniverse_host')
usd_file_path = os.getenv('usd_file_path')


# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print(f"[omni.hello.world] some_public_function was called with {x}")
    return x ** x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[omni.hello.world] MyExtension startup")

        def finish_setup(arg1, arg2):
            manager = omni.kit.app.get_app().get_extension_manager()
            # enable immediately
            manager.set_extension_enabled("msft.nova.robot_controller", True)
            manager.set_extension_enabled("msft.nova.iot_info_panel", True)
            print('finished')

        usd_ctx = omni.usd.get_context()
        stage2load = f"omniverse://{host}/{usd_file_path}"
        if stage2load and len(stage2load) > 0 and (os.path.exists(stage2load) or stage2load.startswith('omniverse:')):
            usd_ctx.open_stage_with_callback(
                stage2load,
                on_finish_fn=finish_setup
            )

        # omni.kit.window.load_layout("MyLayout.json")


        # self._window = ui.Window("My Window", width=300, height=300)
        # with self._window.frame:
        #     with ui.VStack():
        #         label = ui.Label("")


        #         def on_click():
        #             self._count += 1
        #             label.text = f"count: {self._count}"

        #         def on_reset():
        #             self._count = 0
        #             label.text = "empty"

        #         on_reset()

        #         with ui.HStack():
        #             ui.Button("Add", clicked_fn=on_click)
        #             ui.Button("Reset", clicked_fn=on_reset)

        # omni.ui.dock_window_in_window("My Window", "Viewport", omni.ui.DockPosition.BOTTOM, 0.3)

    def on_shutdown(self):
        print("[omni.hello.world] MyExtension shutdown")
