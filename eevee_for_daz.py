from pathlib import Path
import sys
import bpy
from . import easybpy
import json
from enum import Enum, auto
import traceback

KWD_DIFFUSE_TEX = "diffuseTex"


class MaterialGroups(Enum):
    FACE = auto()
    TORSO = auto()
    LEGS = auto()
    ARMS = auto()
    MOUTH = auto()
    EYES = auto()
    PUPILS = auto()
    EYESMOISTURE = auto()
    GENITALS = auto()
    SCLERA = auto()


materialListG8F = {
    "Torso-": MaterialGroups.TORSO,
    "Face-": MaterialGroups.FACE,
    "Lips-": MaterialGroups.FACE,
    "Teeth-": MaterialGroups.MOUTH,
    "Ears-": MaterialGroups.FACE,
    "Legs-": MaterialGroups.LEGS,
    "EyeSocket-": MaterialGroups.FACE,
    "Mouth-": MaterialGroups.MOUTH,
    "Arms-": MaterialGroups.ARMS,
    "Fingernails-": MaterialGroups.ARMS,
    "Sclera-": MaterialGroups.EYES,
    "Toenails-": MaterialGroups.LEGS,
    "Pupils-": MaterialGroups.EYES,
    "EyeMoisture-": MaterialGroups.EYESMOISTURE,
    "Cornea-": MaterialGroups.EYESMOISTURE,
    "Irises-": MaterialGroups.EYES,
}

materialList_r3d = {
    "model_Torso": MaterialGroups.TORSO,
    "model_Face": MaterialGroups.FACE,
    "model_Mouth": MaterialGroups.MOUTH,
    "model_Teeth": MaterialGroups.MOUTH,
    "model_Legs": MaterialGroups.LEGS,
    "model_Toenails": MaterialGroups.LEGS,
    "model_Arms": MaterialGroups.ARMS,
    "model_Fingernails": MaterialGroups.ARMS,
    "model_EyeMoisture": MaterialGroups.EYESMOISTURE,
    "model_Cornea": MaterialGroups.EYESMOISTURE,
    "model_Eyes": MaterialGroups.EYES,
    "model_Genitalia": MaterialGroups.GENITALS,
    "model_Anus:": MaterialGroups.GENITALS,

}

materialList_r3d_inverse = {}

for key, value in materialList_r3d.items():
    if value not in materialList_r3d_inverse:
        materialList_r3d_inverse[value] = []
    materialList_r3d_inverse[value].append(key)


class BetterMaterial:
    def __init__(self, material_remap_ID, material) -> None:
        self.material_remap_ID = material_remap_ID
        self.material = material


class TextureMapping:
    def __init__(self, mappedMaterial=None, originalmaterial=None, diffuseTexture=None) -> None:
        self.material = mappedMaterial
        self.original_material = originalmaterial
        self.diffuse = diffuseTexture


def get_betterMaterial(matID):
    pass


def printJson(object):
    print(json.dumps(object, indent=4, default=lambda x: str(x)))


def has_trailing_numbers(string: str):
    rev = reversed(string)
    hasTrailingNumber = False
    for i, s in enumerate(rev):
        if s.isdigit():
            return True
    return False


def removeSuffixDigits(string: str):
    rev = reversed(string)
    out = string
    for i, s in enumerate(rev):
        if s.isdigit():
            out = out[:-1]
        else:
            break
    return out


def has_any_prefix(string: str, prefixes):
    for prefix in prefixes:
        if string.startswith(prefix):
            return True
    return False


def findDiffuseTextureInMaterial(og_material: bpy.types.Material) -> bpy.types.Node | None:
    principledNode: bpy.types.Node = None

    for node in og_material.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            principledNode = node

            break

    diffuseNode = None
    nextNodes = [principledNode]
    if principledNode is None:
        return None

    while (diffuseNode is None) and (len(nextNodes) >= 1):
        for node in nextNodes.copy():
            nextNodes.remove(node)
            if node is None:
                continue

            if node.type == "TEX_IMAGE":
                diffuseNode = node
                break
            if node == principledNode:
                for link in node.inputs[0].links:
                    nextNodes.append(link.from_node)
            else:
                for input in node.inputs:
                    for link in input.links:
                        nextNodes.append(link.from_node)
    return diffuseNode


def appendMaterial(blendFile: Path, materialName):

    file_path = blendFile.resolve().joinpath("Material", materialName)
    directory_path = file_path.parent

    bpy.ops.wm.append(
        filepath=str(file_path),
        directory=str(directory_path),
        filename=materialName,
        link=False,
        do_reuse_local_id=True,
        set_fake=True
    )
    return bpy.data.materials[materialName]


def findDiffuseNodeInNodeTree(NodeTree: bpy.types.NodeTree):
    for node in NodeTree.nodes:
        if node.label == "Diffuse":
            return node
    return None


def setMaterialTag_DiffuseTexture(material: bpy.types.Material):
    diffuseNode = findDiffuseTextureInMaterial(material)
    if hasattr(diffuseNode, "image"):
        nodeAttrib = diffuseNode.image
    else:
        nodeAttrib = None
    material[KWD_DIFFUSE_TEX] = nodeAttrib


class SMITTY_OT_EeveeForDaz(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "smitty.eevee_for_daz"
    bl_label = "Convert Materials for Daz Characters"
    bl_description = "Convert Materials for Daz Characters"
    bl_options = {"REGISTER", "UNDO"}

    dazG8URL = hash("/data/Daz 3D/Genesis 8/Female/Genesis8Female.dsf#geometry")
    resourcesPath = Path(__file__).parent.joinpath("res/")
    shaders_blendfile_path = resourcesPath.joinpath("shaders.blend")

    dazURLs = [dazG8URL]

    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False

        if context.object.type not in ["MESH"]:
            return False

        return True

    def execute(self, context):
        try:
            self.main(context)
        except Exception as e:
            self.report({"ERROR"}, traceback.format_exc())
            return {"CANCELLED"}
        return {'FINISHED'}

    def main(self, context: bpy.types.Context):
        object = easybpy.active_object()
        # detect shader mappings
        obj_materials = easybpy.get_materials_from_object(object)
        converted_materials = 0
        for material in obj_materials:
            # skip invalid materials by name
            if not has_trailing_numbers(material.name):
                continue

            if not has_any_prefix(material.name, list(materialListG8F.keys())):
                continue

            # tag diffuse texture for this material
            setMaterialTag_DiffuseTexture(material)

            # better_eevee material for this material
            betterMaterialName = materialList_r3d_inverse[materialListG8F[removeSuffixDigits(material.name)]][0]
            betterMaterial = appendMaterial(self.shaders_blendfile_path, betterMaterialName)
            betterMaterial_diffuseNode = findDiffuseNodeInNodeTree(betterMaterial.node_tree)
            if betterMaterial_diffuseNode is not None:
                betterMaterial_diffuseNode.image = material[KWD_DIFFUSE_TEX]

            # replace material in slot
            for slot in object.material_slots:
                if slot.material == material:
                    slot.material = betterMaterial
                    converted_materials += 1
        self.report({"INFO"}, f"Converted {converted_materials} / {len(obj_materials)} materials.")


def menu_func(self, context):
    self.layout.operator(SMITTY_OT_EeveeForDaz.bl_idname, text=SMITTY_OT_EeveeForDaz.bl_label)


def register():
    bpy.utils.register_class(SMITTY_OT_EeveeForDaz)


def unregister():
    bpy.utils.unregister_class(SMITTY_OT_EeveeForDaz)
