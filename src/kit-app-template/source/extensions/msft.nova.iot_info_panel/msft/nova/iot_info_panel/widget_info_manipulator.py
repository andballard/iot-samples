## Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["WidgetInfoManipulator"]

from omni.ui import color as cl
from omni.ui import scene as sc
from omni.kit.viewport.utility import get_active_viewport_window
import omni.ui as ui
import omni.usd
import carb.input
import carb.input
import carb.events
import omni.kit.usd.layers as layers
from pxr import Usd, Sdf, Tf
from .live_edit_session import LiveEditSession
import os

host = os.getenv('omniverse_host')

class _ViewportLegacyDisableSelection:
    """Disables selection in the Viewport Legacy"""

    def __init__(self):
        self._focused_windows = None
        focused_windows = []
        try:
            # For some reason is_focused may return False, when a Window is definitely in fact is the focused window!
            # And there's no good solution to this when mutliple Viewport-1 instances are open; so we just have to
            # operate on all Viewports for a given usd_context.
            import omni.kit.viewport_legacy as vp

            vpi = vp.acquire_viewport_interface()
            for instance in vpi.get_instance_list():
                window = vpi.get_viewport_window(instance)
                if not window:
                    continue
                focused_windows.append(window)
            if focused_windows:
                self._focused_windows = focused_windows
                for window in self._focused_windows:
                    # Disable the selection_rect, but enable_picking for snapping
                    window.disable_selection_rect(True)
        except Exception:
            pass


class _DragPrioritize(sc.GestureManager):
    """Refuses preventing _DragGesture."""

    def can_be_prevented(self, gesture):
        # Never prevent in the middle of drag
        return gesture.state != sc.GestureState.CHANGED

    def should_prevent(self, gesture, preventer):
        if preventer.state == sc.GestureState.BEGAN or preventer.state == sc.GestureState.CHANGED:
            return True


class _DragGesture(sc.DragGesture):
    """"Gesture to disable rectangle selection in the viewport legacy"""

    def __init__(self):
        super().__init__(manager=_DragPrioritize())

    def on_began(self):
        # When the user drags the slider, we don't want to see the selection
        # rect. In Viewport Next, it works well automatically because the
        # selection rect is a manipulator with its gesture, and we add the
        # slider manipulator to the same SceneView.
        # In Viewport Legacy, the selection rect is not a manipulator. Thus it's
        # not disabled automatically, and we need to disable it with the code.
        self.__disable_selection = _ViewportLegacyDisableSelection()

    def on_ended(self):
        # This re-enables the selection in the Viewport Legacy
        self.__disable_selection = None


class WidgetInfoManipulator(sc.Manipulator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._usd_context = omni.usd.get_context()
        # live_session = LiveEditSession(f"omniverse://{host}/Projects/OVPOC/Stages/houston_facility_donut.usd")
        self._stage = self._usd_context.get_stage()
        self.viewport_window = get_active_viewport_window()
        # Acquire input interface
        self.input_interface = carb.input.acquire_input_interface()

        # Get the default app window and its mouse
        app_window = omni.appwindow.get_default_app_window()
        self.mouse = app_window.get_mouse()
        self.is_pinned = False


        # session_layer = self._stage.GetSessionLayer()
        # self.live_layer = live_session.ensure_exists()
        #self.live_layer = Sdf.Layer.FindOrOpen(LIVE_URL)
        #self._usd_context = omni.usd.get_context()
        #self._stage = self._usd_context.get_stage()

        # self._live_syncing = layers.get_live_syncing(self._usd_context)

        # self._layers = layers.get_layers(self._usd_context)
        # self._sessionLayer = self._stage.GetSessionLayer()

        #self._sessionLayer.startTimeCode = 1
        #self._sessionLayer.endTimeCode = 192

        #self._iot_prim = self._stage.GetPrimAtPath("/iot")
        # self.alert = 0


        self.destroy()

        self._root = sc.Transform(visible=False)
        self._radius = 2
        self._distance_to_top = 5
        self._thickness = 2
        self._radius_hovered = 20

    def close(self):
        pass

    def togglePin(self):
        self.is_pinned = not self.is_pinned
        self._widget_header()

    def _widget_header(self):
        with self._ui_header_frame:
            with ui.Stack(ui.Direction.RIGHT_TO_LEFT):
                ui.Button(text=" x ", width=0, height=0, clicked_fn=lambda *args: self.close())
                ui.Button(text="Unpin" if self.is_pinned else "Pin", width=0, height=0, clicked_fn=lambda *args: self.togglePin())
                ui.Spacer()

    def widget_header(self, style={"margin":2}):
        with ui.VStack(height=0,style=style):
            self._ui_header_frame = ui.Frame(name="ui_widget_header_frame")
            self._widget_header()

    def destroy(self):
        self._root = None
        self._slider_subscription = None
        self._name_label = None
        self._name_telemtry1 = None
        self._J0_label_name = None
        self._J0_label_val = None
        self._J1_label_name = None
        self._J1_label_val = None
        self._J2_label_name = None
        self._J2_label_val = None
        self._J3_label_name = None
        self._J3_label_val = None
        self._J4_label_name = None
        self._J4_label_val = None
        self._J5_label_name = None
        self._J5_label_val = None
        self._robot_quality_name = None
        self._robot_quality_val = None
        self._pressure_name = None
        self._pressure_val = None
        self._alert_name = None
        self._alert_val = None
        self._scrollingFrame = None
        self._zstack = None
    # def _on_objects_changed(self, notice, stage):
    #     updated_objects = []
    #     for p in notice.GetChangedInfoOnlyPaths():
    #         updated_objects.append(p)

    #     if len(updated_objects) > 0:
    #         self._update_frame(updated_objects)

    # def _update_frame(self, updated_objects):
    #     # properties = []
    #     for o in updated_objects:
    #         attr = self.live_layer.GetAttributeAtPath(o.pathString)
    #         # properties.append(attr)l
    #         path = str(o.pathString)
    #         if "Vacuum_Alert" in path:
    #             self.alert = str(attr.default)
    #             print(f"default: {self.alert}")
    #         else:
    #             continue

    # create a main windowwindow = ui.create_window(title='Sparkline Example', width=400, height=300)# create a sparkline widgetsparkline = ui.Sparkline(parent=window, name='sparkline', data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])# set the style sheet of the sparkline widgetui.set_style(sparkline, 'Sparkline { line-color: red; line-width: 2px; line-shape: smooth; }')

    def scroll_content(self, event):
        # Get the current scroll position
        scroll_y = self.scrollframe.scroll_y

        # Get the mouse wheel delta
        delta = event.delta

        # Adjust the scroll position by the delta
        scroll_y -= delta

        # Clamp the scroll position to the valid range
        scroll_y = max(0, min(scroll_y, self.scrollframe.scroll_y_max))

        # Set the scroll position
        self.scrollframe.scroll_y = scroll_y

    def _on_build_widgets(self):
        def on_mouse_wheel(self, x, y, modifier):
            if modifier == carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT:
                # scroll horizontally
                scroll_x = max(0, min(self._scrollingFrame.scroll_x - x, self._scrollingFrame.scroll_x_max))
                self._scrollingFrame.scroll_here(scroll_x, self._scrollingFrame.scroll_y)
            else:
                # scroll vertically
                scroll_y = max(0, min(self._scrollingFrame.scroll_y - y, self._scrollingFrame.scroll_y_max))
                self._scrollingFrame.scroll_here(self._scrollingFrame.scroll_x, scroll_y)
        # self.viewport_window.frame.set_mouse_wheel_fn(on_mouse_wheel)

        self._placer = ui.Placer(draggable=True)
        with self._placer:
            with self.widget_header():
                self._zstack = ui.ZStack()
                self._scrollingFrame = ui.ScrollingFrame(
                        style={
                            "background_color": cl("#000000bf"),
                            "border_width": 10,
                            "border_color": cl(0.7),
                            "border_radius": 4,
                            "scrollbar_policy": ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                            "scrollbar_width": 100,
                            "scrollbar_color": cl(0.9),
                            "scrollbar_background_color": cl(0.3),
                        }
                    )
                with self._zstack:
                    self._scrollingFrame
                        # with ui.Frame():
                        #     # Create a grid layout manager
                        #     with ui.Grid(ui.Direction.TOP_TO_BOTTOM, selected=True):
                        #     # Add some labels to the grid
                        #         for i in range(40):
                        #             with ui.HStack(width=0):
                        #                 self._J1_label_name = ui.Label(f"J{i}", name="prop_label", word_wrap=True, width=100)
                    # self._rectangle = ui.Rectangle(
                    #     width=800,
                    #     height=800,
                    #     style={
                    #         "background_color": cl("#000000bf"),
                    #         "border_color": cl(0.7),
                    #         "border_width": 0,
                    #         "border_radius": 4,
                    #     }
                    # )

                    self._mainFrame = ui.Frame()
                    with self._mainFrame:
                        with ui.VStack(style={"font_size": 28,"margin": 8}):
                            # ui.Button(text=" x ", width=0, height=0, clicked_fn=lambda *args: self.close(), alignment=ui.Alignment.RIGHT)
                            ui.Spacer(height=2)
                            self._name_label = ui.Label("", height=0, alignment=ui.Alignment.CENTER)
                            # sparkline = ui.Sparkline(parent=window, name='sparkline', data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
                            # data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
                            # with ui.HStack():
                            #     ui.Spacer(width=200) # align the sparklines with the scrollable frame
                            #     for value in data:
                            #         with ui.VStack():
                            #             ui.Sparkline(
                            #                 data=[value],
                            #                 style={
                            #                     "sparkline_type": 0,
                            #                     "sparkline_color": cl(0.9),
                            #                     "sparkline_width": 2,
                            #                     "marker_color": cl(0.9),
                            #                     "marker_size": 4,
                            #                     "show_markers": True,
                            #                 },
                            #             )
                            #         ui.Label(str(value), alignment=ui.Alignment.CENTER)

                            with ui.HStack(width=0):
                                self._J0_label_name = ui.Label("J0", name="prop_label", word_wrap=True, width=100)
                                self._J0_label_val = ui.Label("", name="prop_value")
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
                                self._alert_val = ui.Label("", name="prop_value")

                                # ui.Spacer(height=2)
                                # self._name_telemtry1 = ui.Label("", height=0, alignment=ui.Alignment.CENTER)

                                # ui.Spacer(height=10)

        self._scrollingFrame.add_child(self._mainFrame)
        # self._scrollingFrame.scroll_only_window_hovered = False
        # self._scrollingFrame.set_mouse_wheel_fn(on_mouse_wheel)
        # self._scrollingFrame.scroll_here(0, 1)

        # self._scrollingFrame.set_scroll_y_changed_fn(on_mouse_wheel)

        # Set the functions to be called when the scroll bars are moved
        self._scrollingFrame.set_scroll_x_changed_fn(lambda x: print(f"Horizontal scroll bar moved to {x}"))
        self._scrollingFrame.set_scroll_y_changed_fn(lambda y: print(f"Vertical scroll bar moved to {y}"))



        # Register the function to be called when a mouse wheel event occurs
        # carb.events.register_listener(self.handle_mouse_wheel, "carb.input.mouse.wheel")

        # self._scrollingFrame = ui.ScrollingFrame
        # self._scrollingFrame.set_mouse_wheel_fn(on_mouse_wheel)


        self.on_model_updated(None)

        # Additional gesture that prevents Viewport Legacy selection
        self._widget.gestures += [_DragGesture()]

        self.listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, self._stage)

    # def close(self):
    #     self._root.visible = False
    #     if self.listener is not None:
    #         self.listener.Revoke()
    #         self.listener = None

    # Function to handle mouse wheel events
    def handle_mouse_wheel(self):
        # Get the mouse wheel scroll value
        scroll_value = self.input_interface.get_mouse_value(self.mouse, carb.input.MouseInput.SCROLL_UP)
        # If the mouse wheel is scrolled, adjust the scroll bar position
        if scroll_value:
            self._scrollingFrame.scroll_y -= scroll_value * 0.1  # Adjust this value as needed

    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        self._root = sc.Transform(visible=False)
        with self._root:
            with sc.Transform(scale_to=sc.Space.SCREEN):
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 100, 0)):
                    # Label
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        self._widget = sc.Widget(600, 405, update_policy=sc.Widget.UpdatePolicy.ALWAYS)
                        self._widget.frame.set_build_fn(self._on_build_widgets)

    def on_model_updated(self, _):
        # if we don't have selection then show nothing
        if not self.model or not self.model.get_item("name"):
            # self._root.visible = False
            self.listener = None
            return

        # Update the shapes
        position = self.model.get_as_floats(self.model.get_item("position"))
        self._root.transform = sc.Matrix44.get_translation_matrix(*position)
        self._root.visible = True

        # Update the slider
        def update_scale(prim_name, value):
            print(f"changing scale of {prim_name}, {value}")


        # Update the shape name
        if self._name_label:
            self._name_label.text = f"Prim:{self.model.get_item('name')}"

        # if self._quality_label_val:
        #     self._name_label.text = f"Prim:{self.model.get_item('name')}"

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
                prim = self._stage.GetPrimAtPath(o.pathString.split('.')[0])
                attr = prim.GetAttribute(o.pathString.split('.')[1])
                if attr is None:
                    continue

                val = str(attr.Get())
                # path = str(o.pathString)
                if 'j0' in o.pathString:
                    self._J0_label_val.text = val
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