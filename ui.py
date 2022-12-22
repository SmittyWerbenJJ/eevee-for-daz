import bpy
from . import easybpy
import bpy.utils.previews
import os


DAZ_ICON_NAME = "daz_icon"
PCOL_MAIN = "main"
ICON_DAZ = "icon_daz"
preview_collections = {}


class SMITTY_MT_EeveeForDaz(bpy.types.Menu):
    """Creates a Panel in the Object properties window"""

    bl_label = "Convert Materials for Daz Characters"
    bl_idname = "SMITTY_MT_EeveeForDaz"

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.operator("smitty.eevee_for_daz")


def eeveeForDaz_menu_functions(self, context):
    layout = self.layout
    my_icon = preview_collections[PCOL_MAIN][ICON_DAZ]
    layout.menu(
        SMITTY_MT_EeveeForDaz.bl_idname,
        icon_value=my_icon.icon_id
    )


def register_icons():
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    pcoll = bpy.utils.previews.new()
    pcoll.load(ICON_DAZ, os.path.join(my_icons_dir, "daz_icon.png"), 'IMAGE')

    preview_collections[PCOL_MAIN] = pcoll


def unregister_icons():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()


def register():
    register_icons()
    bpy.utils.register_class(SMITTY_MT_EeveeForDaz)
    bpy.types.MATERIAL_MT_context_menu.append(eeveeForDaz_menu_functions)
    # unregister_icons()
    # bpy.utils.unregister_class(SMITTY_MT_EeveeForDaz)


def unregister():
    unregister_icons()
    bpy.utils.unregister_class(SMITTY_MT_EeveeForDaz)
    bpy.types.MATERIAL_MT_context_menu.remove(eeveeForDaz_menu_functions)
