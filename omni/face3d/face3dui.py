
import carb
import omni
import os
import time
from omni.kit.widget.settings import create_setting_widget, create_setting_widget_combo, SettingType
import omni.ui as ui
from pxr import Gf
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
                        upload_button.set_clicked_fn(self._on_image_select_click())

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
            fileid = int(time.time())
            filename = f'%d.zip' % fileid
            tmp_filepath = os.path.join(os.path.expanduser("~/Pictures"), filename)
            ret = filehelper.download_file(tmp_filepath, url)
            if ret:
                obj_filepath = filehelper.unzip_file(tmp_filepath)
                filename = f'%d.usd' % fileid
                usd_filepath = os.path.join(os.path.expanduser("~/Pictures"), filename)
                filehelper.convert(obj_filepath, usd_filepath)