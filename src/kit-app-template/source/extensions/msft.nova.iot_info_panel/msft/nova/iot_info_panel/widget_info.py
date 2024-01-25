import omni.ui as ui
import omni.usd
import time
import statistics
from threading import Timer
from omni.ui import color as cl
from pxr import Usd, Tf, UsdGeom, UsdShade


class InfoWidgetProvider():
    """
        Info widget, showing a list of properties in a kkey value structure
    """

    def __init__(self):
        self.start = time.time()
        self.end = time.time()
        self.is_pinned = False
        self.history = [0.0]
        self.usd_context = omni.usd.get_context()
        self.stage = self.usd_context.get_stage()
        self.stage_event_sub = omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_event, name="Object Info Selection Update"
        )

    def _on_kit_selection_changed(self):
        # selection change, reset it for now

        self._current_path = ""

        if not self.stage:
            return

        prim_paths = self.usd_context.get_selection().get_selected_prim_paths()
        # if not prim_paths:
        #     self._item_changed(self.position)
        #     # Revoke the Tf.Notice listener, we don't need to update anything
        #     if self._stage_listener:
        #         self._stage_listener.Revoke()
        #         self._stage_listener = None
        #     return

        prim = self.stage.GetPrimAtPath(prim_paths[0])

        if prim.IsA(UsdGeom.Imageable):
            if '/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1' in prim_paths[0]:
                material, relationship = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
                if material:
                    self.material_name = str(material.GetPath())
                else:
                    self.material_name = "N/A"

                self._placer.visible = True
        else:
            self._prim = None
            return

        self._prim = prim
        self._current_path = prim_paths[0]

    def _on_stage_event(self, event):
        """Called by stage_event_stream"""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_kit_selection_changed()

    _whitelisted_props = (
        # allowed list of properties
    )

    def _order_and_filter_data(self):
        records = dict.copy(self._data)
        if self._whitelisted_props:
            records = dict((k, v) for k, v in records.items() if k in self._whitelisted_props)
        result = dict(sorted(records.items(), key=lambda kv: kv[0]))
        return result

    def _widget_header(self):
        with self._ui_header_frame:
            with ui.Stack(ui.Direction.RIGHT_TO_LEFT):
                ui.Button(text=" X ", width=0, height=0, clicked_fn=lambda *args: self.close(), alignment = ui.Alignment.RIGHT, style={"font":"${fonts}/OpenSans-SemiBold.ttf", "font_size": 60.0})
                ui.Label("IoT Data", name="prop_label", word_wrap=True, width=430, alignment=ui.Alignment.CENTER, style={"font":"${fonts}/OpenSans-SemiBold.ttf", "font_size": 40.0})

                #ui.Button(text="Unpin" if self.is_pinned else "Pin", width=0, height=0, clicked_fn=lambda *args: self.togglePin())
                ui.Spacer()

    def widget_header(self, style={"margin":2}):
        with ui.VStack(height=10,style=style):
            self._ui_header_frame = ui.Frame(name="ui_widget_header_frame")
            self._widget_header()

    def close(self):
        self._placer.visible = False

    def togglePin(self):
        self.is_pinned = not self.is_pinned
        self._widget_header()

    def build_widget(self, viewport_window):
        self._placer = ui.Placer(visible = False, draggable=True, offset_x=100, offset_y = 100)
        with self._placer:
            with ui.ZStack(width=550, height=10, style={"margin":2}):
                ui.Rectangle(
                    style={
                        # "background_color": cl(0.2),
                        "background_color": cl("#000670bf"), #111eff   #00089f
                        "border_color": cl("#00055c"),
                        "border_width": 1,
                        "border_radius": 4,
                    }
                )

                with ui.VStack(height=10):
                    self.widget_header()
                    self._render_body()

    def _render_body(self):
        #self._zstack = ui.ZStack(height = 50)
        self._scrollingFrame = ui.ScrollingFrame(
                style={
                    "background_color": cl("#000670bf"),
                    "border_width": 10,
                    "border_color": cl(0.7),
                    "border_radius": 4,
                    "scrollbar_policy": ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    "scrollbar_width": 100,
                    "scrollbar_color": cl(0.9),
                    "scrollbar_background_color": cl(0.3),
                }
            )
        self._scrollingFrame.height = ui.Length(300)
        with self._scrollingFrame:
            with ui.VStack(style={"font_size": 28,"margin": 8}, height = 50):
                with ui.HStack():
                    self._J0_label_name = ui.Label("J0", name="prop_label", word_wrap=True, width=100)
                    self._J0_label_val = ui.Label("", name="prop_value")

                    # Add data to the plot
                    # self.plot.set_data([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
                    # set_data = [1.0, 2.0, 3.0, 4.0, 5.0]
                    #self.plot = ui.Plot(type=ui.Type.LINE, scale_min=0, scale_max=10)

                    # for i in range(5):
                    #     set_data.append(math.cos(math.radians(i)))

                    self._plot = ui.Plot(ui.Type.LINE, -60.0, 1.0, width=180, height=100, style={"color": cl.white, "border_width": 3})
                    #self._j0_arrow = ui.Image("", width=ui.Length(90), height=ui.Length(100), style={"border_width": 0})
                    #self._plot.set_data(*set_data)
                with ui.HStack(width=0):
                    self._J1_label_name = ui.Label("J1", name="prop_label", word_wrap=True, width=100)
                    self._J1_label_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._J2_label_name = ui.Label("J2", name="prop_label", word_wrap=True, width=100)
                    self._J2_label_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._J3_label_name = ui.Label("J3", name="prop_label", word_wrap=True, width=100)
                    self._J3_label_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._J4_label_name = ui.Label("J4", name="prop_label", word_wrap=True, width=100)
                    self._J4_label_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._J5_label_name = ui.Label("J5", name="prop_label", word_wrap=True, width=100)
                    self._J5_label_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._robot_quality_name = ui.Label("quality", name="prop_label", word_wrap=True, width=100)
                    self._robot_quality_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._pressure_name = ui.Label("pressure", name="prop_label", word_wrap=False, width=100)
                    self._pressure_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._alert_name = ui.Label("alert", name="prop_label", word_wrap=True, width=100)
                    self._alert_val = ui.Label("alert", name="prop_value", word_wrap=True, width=100)

        self.listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, self.stage)

    def addlabel(self):
        self._hs1 = ui.HStack(width=0)
        with self._hs1:
            self._J0_label_name = ui.Label("J0", name="prop_label", word_wrap=True, width=100)
            self._J0_label_val = ui.Label("", name="prop_value")
        return self._hs1

    def _on_objects_changed(self, notice, stage):
        updated_objects = []
        for p in notice.GetChangedInfoOnlyPaths():
            if "Value" in str(p.pathString):
                updated_objects.append(p)

        if len(updated_objects) > 0:
            self._update_frame(updated_objects)

    def _update_frame(self, updated_objects):
        path = None
        try:
            for o in updated_objects:
                path = o.pathString
                prim = self.stage.GetPrimAtPath(o.pathString.split('.')[0])
                attr = prim.GetAttribute(o.pathString.split('.')[1])
                if attr is None:
                    continue

                val = str(round(float(attr.Get()), 2))
                # path = str(o.pathString)
                if 'j0' in o.pathString:
                    self._J0_label_val.text = val
                    if len(self.history) < 500:
                        self.history.append(float(val))
                    else:
                        self.history.pop(0)
                        self.history.append(float(val))

                    self._j0_last_avg = statistics.fmean(self.history)

                    self.end = time.time()
                    if self.end - self.start >= 10:
                        # if self._j0_last_avg >= statistics.fmean(self.history):
                        #     self._j0_arrow = ui.Image("trending_up_arrow.png", width=ui.Length(90), height=ui.Length(100), style={"border_width": 0})
                        # else:
                        #     self._j0_arrow = ui.Image("trending_down_arrow.png", width=ui.Length(90), height=ui.Length(100), style={"border_width": 0})
                        # self.listener.Revoke()
                        # self.listener = None
                        # self._render_body()
                        self._plot.scale_min = min(self.history)
                        self._plot.scale_max = max(self.history)
                        self._plot.set_data(*self.history)
                        self.start = self.end
                elif 'j1' in o.pathString:
                    self._J1_label_val.text = val
                elif 'j2' in o.pathString:
                    self._J2_label_val.text = val
                elif 'j3' in o.pathString:
                    self._J3_label_val.text = val
                elif 'j4' in o.pathString:
                    self._J4_label_val.text = val
                elif 'j5' in o.pathString:
                    self._J5_label_val.text = val
                elif 'quality' in o.pathString:
                    self._robot_quality_val.text = val
                elif 'pressure' in o.pathString:
                    self._pressure_val.text = val
                elif 'alert' in o.pathString:
                    self._alert_val.text = val
                else:
                    continue
        except Exception as e:
            print(f'Failed to update frame {path} with error: {e}')