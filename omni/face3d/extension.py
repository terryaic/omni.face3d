import omni.ext
import omni.ui as ui
from . import face3dui

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[omni.face3d] MyExtension startup")

        self.ui = face3dui.Face3dUI()

    def on_shutdown(self):
        print("[omni.face3d] MyExtension shutdown")
