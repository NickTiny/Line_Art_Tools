import bpy


class LINE_ART_TOOLS_OT_base_class(bpy.types.Operator):
    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.mode == "OBJECT"


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


def sync_lr_to_strip_create(item, scene):
    obj = item.object
    obj.animation_data_create()
    for strip in scene.sequence_editor.sequences_all:
        item.object.grease_pencil_modifiers[item.lr_mod].keyframe_insert(
            "thickness", frame=strip.frame_final_start
        )
    for fcurve in obj.animation_data.action.fcurves:
        set_keyframe_type(fcurve, "constant")


def get_keyframe_type(fcurve: bpy.types.FCurve):
    for kf in fcurve.keyframe_points:
        kf.interpolation != "CONSTANT"
        return False
    return True


def set_keyframe_type(fcurve: bpy.types.FCurve, type="CONSTANT"):
    for kf in fcurve.keyframe_points:
        kf.interpolation = "CONSTANT"


def check_anim_is_constant(obj: bpy.types.Object) -> bool:
    """Check all keyframe points on object are constant interpolation"""
    for fcurve in obj.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            if kf.interpolation != "CONSTANT":
                return False
    return True


def sync_line_art_obj_to_strip(
    obj: bpy.types.Object, strip: bpy.types.Sequence
) -> bool:
    """Sync Line Art Keyframes to Strip's frame start"""
    if not (obj.animation_data and obj.animation_data.action):
        return False
    if check_anim_is_constant(obj) == False:
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


def get_line_art_keyframes(object: bpy.types.Object):
    return object.animation_data.action.fcurves[0].keyframe_points


def clear_rogue_keyframes(item, strip):
    strip_end = strip.frame_final_end
    strip_start = strip.frame_final_start
    mod = item.object.grease_pencil_modifiers[item.lr_mod]
    keyframes = get_line_art_keyframes(item.object)
    for key in keyframes:
        if key.co[0] in range(strip_start, strip_end):
            if key.co[0] == strip_start:
                key.co[1] = item.thickness
            if key.co[0] in range(strip_start + 1, strip_end):
                mod.keyframe_delete("thickness", frame=key.co[0])


def set_seq_line_art_thickness(item, strip: bpy.types.Sequence) -> bool:
    """Set thickness of Seq Line Art for a strip"""
    mod = item.object.grease_pencil_modifiers[item.lr_mod]
    keyframe = mod.keyframe_insert("thickness", frame=strip.frame_final_start)
    clear_rogue_keyframes(item, strip)
    return keyframe


class LINE_ART_TOOLS_OT_enable_animation(LINE_ART_TOOLS_OT_base_class):
    bl_idname = "linearttools.enable_animation"
    bl_label = "Enable Animation on Object"
    bl_description = "TODO"
    bl_options = {"UNDO"}

    index: bpy.props.IntProperty(name="index", default=0)

    def execute(self, context):
        scene = context.window_manager.edit_scene
        line_art_tools_items = context.window_manager.line_art_tools_items
        item = line_art_tools_items[self.index]
        sync_lr_to_strip_create(item, scene)
        line_art_tools_items[self.index].sync_to_strips = True
        return {"FINISHED"}


class SEQUENCER_PT_line_art(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_idname = "SEQUENCER_PT_line_art_tools"
    bl_label = "Active Strip Line Art"
    bl_category = "Tiny Sequence Tools"

    def all_status_true(context):
        for item in context.scene.line_art_load.load:
            if item.status == False:
                return False
        return True

    def get_keyframe_icon(bool):
        if bool:
            return "KEYFRAME_HLT"
        else:
            return "KEYFRAME"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=False)
        row = col.row(align=True)
        line_art_tools_items = context.window_manager.line_art_tools_items
        # row.prop(context.window_manager, "line_art_cam_override", text="")
        # row.label(text="Override Line Art Camera", icon="CAMERA_DATA")
        row = col.row(align=True)
        col = layout.box()
        row = col.row(align=False)
        # row.label(text="Sequence Line Art Items", icon="MOD_LINEART")
        # row.operator("view3d.check_line_art_obj", icon="ERROR", text="Check Line Art")
        # row.operator("view3d.update_similar_strip_line_art", icon="DUPLICATE", text="")
        # row.operator("view3d.refresh_line_art_obj", icon="FILE_REFRESH", text="")
        row.prop(context.window_manager, "edit_scene")
        # if context.active_sequence_strip is None:
        #     return
        for index, item in enumerate(line_art_tools_items):
            box = col.box()
            row = box.row(align=False)
            prop = row.operator(
                "linearttools.enable_animation",
                icon=get_keyframe_icon(line_art_tools_items[index].sync_to_strips),
                text="",
            )
            prop.index = index

            row.prop(
                item,
                "thickness",
                slider=False,
                expand=False,
                text=item.object.name.split("LAT_")[-1],
            )
            row.prop(
                item,
                "viewport",
                icon="RESTRICT_VIEW_OFF",
                text="",
            )
            props = row.operator(
                "linearttools.open_properties", icon="MOD_LINEART", text=""
            )
            props.index = index
            props = row.operator("linearttools.copy_mod", icon="DUPLICATE", text="")
            props.index = index
            props = row.operator(
                "linearttools.remove_gp", text="", icon="X", emboss=False
            )
            props.index = index
        if not len(line_art_tools_items) >= 1:
            row.label(text="No Objects Found!")


def get_keyframe_icon(bool):
    if bool:
        return "KEYFRAME_HLT"
    else:
        return "KEYFRAME"


classes = (LINE_ART_TOOLS_OT_enable_animation, SEQUENCER_PT_line_art)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
