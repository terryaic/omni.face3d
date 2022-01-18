
import carb
import omni
import os
import time
from omni.kit.widget.settings import create_setting_widget, create_setting_widget_combo, SettingType
import omni.ui as ui
from pxr import Gf,UsdGeom
import asyncio
from . import filehelper

EXTENSION_NAME = "Face3D"

class Face3dUI:
    def __init__(self):
        self._window = ui.Window(EXTENSION_NAME, width=600, height=800, menu_path=f"Window/{EXTENSION_NAME}")
        self._window.deferred_dock_in("Property")
        self._build_ui()

    def _build_ui(self):
        """ Add Shape Settings """
        with self._window.frame:
            with ui.CollapsableFrame(title="Upload photo"):
                with ui.VStack(spacing=2):
                    with ui.HStack(height=20):
                        ui.Label("select photo", word_wrap=True, width=ui.Percent(35))
                        upload_button = omni.ui.Button("Add", height=5, style={"padding": 12, "font_size": 20})
                        upload_button.set_clicked_fn(self._on_image_select_click)

    def _on_filepicker_cancel(self, *args):
        self._filepicker.hide()
        
    def _on_filter_item(self, item):
        file_exts = ["png", "PNG", "jpg", "JPG", "jpeg", "JPEG"]
        for fex in file_exts:
            if item.name.endswith(fex) or item.is_folder:
                return True
                
    async def _on_selection(self, filename, dirname):
        selections = self._filepicker.get_current_selections()
        # Handle case where user clicks and highlights directory to load
        if selections and not filename and os.path.isdir(selections[0]):
            dirname = selections[0]
        path = f"{dirname}/{filename}" if dirname else filename
        if os.path.isfile(path):
            selected_mesh = await self.upload(path)
        self._filepicker.hide()
        self._window.frame.rebuild()
        
    def _on_image_select_click(self):
        """
        Show filepicker after image select is clicked
        """
        filters = [
            "All Supported Files (*.png, *.jpg, ...)",
            "png Files (*.png)",
            "jpg Files (*.jpg)",
            "jpeg Files (*.jpeg)",
        ]

        self._filepicker = omni.kit.window.filepicker.FilePickerDialog(
            f"{EXTENSION_NAME}/Select Image",
            click_apply_handler=lambda f, d: asyncio.ensure_future(self._on_selection(f, d)),
            click_cancel_handler=self._on_filepicker_cancel,
            item_filter_options=filters,
            item_filter_fn=self._on_filter_item,
        )
        self._filepicker.navigate_to(os.path.expanduser("~/Pictures"))  # TODO: use cached dir path
        self._filepicker.refresh_current_directory()

    async def upload(self, filepath):
        url = filehelper.upload_file(filepath)
        if url:
            outpath = os.path.expanduser("~/Pictures")
            ret = filehelper.download_file(outpath, url)
            if ret:
                filename = os.path.basename(ret)
                filename = filename[:filename.rfind(".")]
                obj_filepath = filehelper.unzip_file(ret, outpath)
                obj_filepath = os.path.join(obj_filepath, filename + ".obj.obj")
                usd_filename = filename + ".usd"
                usd_filepath = os.path.join(os.path.join(outpath, filename), usd_filename)
                await filehelper.convert(obj_filepath, usd_filepath)
                self.insert_into_scene(usd_filepath, 1)

    def insert_into_scene(self, usd_filepath, scale):
        stage = omni.usd.get_context().get_stage()
        prim_path = str(stage.GetDefaultPrim().GetPath())
        over_path = prim_path + "/face"
        over = stage.OverridePrim(over_path)
        over.GetReferences().AddReference(usd_filepath)

        metersPerUnit = UsdGeom.GetStageMetersPerUnit(stage)
        scaled_scale = scale / metersPerUnit
        pos = Gf.Vec3d(0,0,0)
        rot = Gf.Rotation(Gf.Vec3d(0,0,0), 0)
        addobject_fn(over.GetPath(), pos, rot, scaled_scale)
        
# Got this From Lou Rohan... Thanks Lou!
# objectpath - path in omniverse - omni:/Projects/Siggraph2019/AtticWorkflow/Props/table_cloth/table_cloth.usd
# objectname - name you want it to be called in the stage
# xform - Gf.Matrix4d
def addobject_fn(path, position, rotation, scale):
    # The original model was translated by the centroid, and scaled to be normalized by the length of the
    # hypotenuse of the bbox
    translate_mtx = Gf.Matrix4d()
    rotate_mtx = Gf.Matrix4d()
    scale_mtx = Gf.Matrix4d()

    translate_mtx.SetTranslate(position)  # centroid/metersPerUnit)
    rotate_mtx.SetRotate(rotation)
    scale_mtx = scale_mtx.SetScale(scale)
    transform_matrix = scale_mtx * rotate_mtx * translate_mtx

    omni.kit.commands.execute("TransformPrimCommand", path=path, new_transform_matrix=transform_matrix)
