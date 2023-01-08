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


def sync_strip_camera_to_seq_line_art(strip: bpy.types.Sequence) -> bool:
    """Set Sequence Line Art Object's Camera to Strip Camera"""
    scene = strip.scene
    wm = bpy.context.window_manager
    if not wm.line_art_cam_override and wm.use_seq_line_art:
        for item in wm.line_art_seq_items:
            if len(item.object.users_scene) >= 1:
                obj = item.object
                obj.grease_pencil_modifiers[
                    "SEQ_LINE_ART"
                ].source_camera = strip.scene_camera
                return True
    return False


def get_object_animation_is_constant(obj: bpy.types.Object) -> bool:
    """Check all keyframe points on object are constant interpolation"""
    if obj.animation_data.action is None:
        return False
    for fcurve in obj.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            if kf.interpolation != "CONSTANT":
                return False
    return True


def sync_line_art_obj_to_strip(
    obj: bpy.types.Object, strip: bpy.types.Sequence
) -> bool:
    """Sync Line Art Keyframes to Strip's frame start"""
    if get_object_animation_is_constant(obj) == False:
        return False
    fcurves = obj.animation_data.action.fcurves
    keyframes = fcurves[0].keyframe_points
    keyframes = sorted(keyframes, key=lambda i: i.co[0], reverse=False)
    for key in keyframes:
        if key.co[0] in range(strip.frame_final_start, strip.frame_final_end):
            if key.co[0] != strip.frame_final_start:
                return False
    return True


def set_line_art_animation_to_constant(
    context: bpy.types.Context, line_art_mod: bpy.types.ObjectGpencilModifiers
):
    """Insert Line Art Keyframes at Strip's frame start"""
    for strip in context.scene.sequence_editor.sequences_all:
        line_art_mod.keyframe_insert("thickness", frame=strip.frame_final_start)

    for fcurve in line_art_mod.id_data.original.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = "CONSTANT"


def set_seq_line_art_thickness(
    obj: bpy.types.Object, thickness: int, strip: bpy.types.Sequence
) -> bool:
    """Set thickness of Seq Line Art for a strip"""
    set_thickness = False
    strip_start = strip.frame_final_start
    strip_end = strip.frame_final_end

    fcurves = obj.animation_data.action.fcurves
    keyframes = fcurves[0].keyframe_points
    line_art_mods = [
        mod for mod in obj.grease_pencil_modifiers if mod.type == "GP_LINEART"
    ]
    for mod in line_art_mods:
        mod.thickness = thickness
        mod.keyframe_insert("thickness", frame=strip_start)
        set_thickness = True

    for key in keyframes:
        if key.co[0] in range(strip_start, strip_end):
            if key.co[0] == strip_start:
                key.co[1] = thickness
            if key.co[0] in range(strip_start + 1, strip_end):
                for mod in line_art_mods:
                    mod.keyframe_delete("thickness", frame=key.co[0])

    return set_thickness
