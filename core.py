import bpy

col_name = "Line Art Tool Objects"


def get_line_art_tools_collection(context):
    # Find existing Collection
    collection = None
    for col in context.scene.collection.children:
        if col_name in col.name:
            collection = col
    if not collection:
        collection = bpy.data.collections.new(col_name)
        context.scene.collection.children.link(collection)
    return collection


def get_gp_modifier_by_name(obj: bpy.types.Object, name: str):
    """Return GP Modifer"""
    if obj.grease_pencil_modifiers:
        for mod in obj.grease_pencil_modifiers:
            if mod.name == name:
                return mod
    return


def get_gp_modifier_by_type(obj: bpy.types.Object, name: str):
    """Return GP Modifer"""
    if obj.grease_pencil_modifiers:
        for mod in obj.grease_pencil_modifiers:
            if mod.type == name:
                return mod
    return


def line_art_tools_item_add(line_art_tools, obj):
    """Object must have exactly one Line Art Modifier"""
    line_art_tool_item = line_art_tools.add()
    line_art_tool_item.object = obj
    obj.line_art_tools_obj = True
    line_art_mod = get_gp_modifier_by_type(obj, "GP_LINEART")
    line_art_mod.name = line_art_tool_item.lr_mod
    if not get_gp_modifier_by_name(obj, line_art_tool_item.thick_mod):
        obj.grease_pencil_modifiers.new(line_art_tool_item.thick_mod, "GP_THICK")
    return line_art_tool_item


def line_art_tools_remove(line_art_tools, obj):
    status = False
    if not obj.grease_pencil_modifiers:
        return status
    for index, item in enumerate(line_art_tools):
        if item.object == obj:
            lr_mod = get_gp_modifier_by_name(obj, line_art_tools[index].thick_mod)
            obj.grease_pencil_modifiers.remove(lr_mod)
            line_art_tools.remove(index)
            obj.line_art_tools_obj = False
            status = True
    return status


def line_art_tools_refresh(line_art_tools):
    line_art_tools.clear()
    for obj in bpy.data.objects:
        if obj.line_art_tools_obj and len(obj.users_scene) != 0:
            line_art_tools_item_add(line_art_tools, obj)
    return
