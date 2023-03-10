import bpy


def check_gp_obj_modifiers(obj):
    if obj.grease_pencil_modifiers:
        return True
    return False


class lr_seq_items(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(type=bpy.types.Object)


class LINE_ART_TOOLS_props(bpy.types.PropertyGroup):
    def get_thickness(self):
        obj = self.object
        if obj.grease_pencil_modifiers:
            return int(obj.grease_pencil_modifiers[self.lr_mod].thickness)
        return 0

    def set_thickness(self, thickness: int):
        scene = bpy.data.window_managers[0].edit_scene
        self.object.grease_pencil_modifiers[self.lr_mod].thickness = thickness
        if self.sync_to_strips:
            from .pro import set_seq_line_art_thickness

            if scene.sequence_editor and scene.sequence_editor.active_strip:
                strip = scene.sequence_editor.active_strip
                set_thick_done = set_seq_line_art_thickness(self, strip)
                return

    def get_thickness_offset(self):
        items = bpy.data.window_managers[0].line_art_tools_items
        thick_list = []
        for item in items:
            obj = item.object
            if (
                check_gp_obj_modifiers(obj)
                and obj.type == "GPENCIL"
                and len(obj.users_scene) != 0
            ):
                thick_list.append(
                    obj.grease_pencil_modifiers[item.thick_mod].thickness_factor
                )
        if len(set(thick_list)) == 1:
            return thick_list[0]
        else:
            return -1

    def set_thickness_offset(self, thickness_factor: int):
        obj = self.object
        items = bpy.data.window_managers[0].line_art_tools_items
        for item in items:
            obj = item.object
            if (
                check_gp_obj_modifiers(obj)
                and obj.type == "GPENCIL"
                and len(obj.users_scene) != 0
            ):
                obj.grease_pencil_modifiers[
                    item.thick_mod
                ].thickness_factor = thickness_factor
        return

    def get_viewport(self):
        obj = self.object
        if check_gp_obj_modifiers(obj):
            if self.object.grease_pencil_modifiers[self.lr_mod]:
                return self.object.grease_pencil_modifiers[self.lr_mod].show_viewport
        return

    def set_viewport(self, val: bool):
        self.object.grease_pencil_modifiers[self.lr_mod].show_viewport = val

    def get_objects(self):
        for obj in bpy.data.objects:
            if obj == bpy.context.active_object:
                return obj

    def get_status(self):
        scene = bpy.context.scene
        obj = self.object
        if self.sync_to_strips:
            from .pro import sync_line_art_obj_to_strip

            if scene.sequence_editor and scene.sequence_editor.active_strip:
                strip = scene.sequence_editor.active_strip
                if strip:
                    return sync_line_art_obj_to_strip(self.object, strip)
        return 0

    object: bpy.props.PointerProperty(type=bpy.types.Object)
    lr_mod: bpy.props.StringProperty(default="Line Art Tools - Line Art")
    thick_mod: bpy.props.StringProperty(default="Line Art Tools - Offset Thickness")
    thickness_offset: bpy.props.FloatProperty(
        name="thickness offset",
        get=get_thickness_offset,
        set=set_thickness_offset,
        options=set(),
    )
    thickness: bpy.props.IntProperty(
        name="Line Art Seq",
        default=0,
        get=get_thickness,
        set=set_thickness,
        options=set(),
    )
    viewport: bpy.props.BoolProperty(
        name="Viewport Display Seq Line Art",
        get=get_viewport,
        set=set_viewport,
        options=set(),
        description="Hide and Show Line Art Modifiers in Viewports",
    )

    status: bpy.props.BoolProperty(
        name="Keyframe Sync Status",
        get=get_status,
        description="Line Art keyframes are out of sync with the sequencer, please update by adjusting the thickness to update keyframes or adjust manually.",
    )

    sync_to_strips: bpy.props.BoolProperty(
        name="Sync to Strips",
        description="TODO",
        default=False,
    )


classes = (lr_seq_items, LINE_ART_TOOLS_props)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.line_art_tools_items = bpy.props.CollectionProperty(
        type=LINE_ART_TOOLS_props
    )
    bpy.types.WindowManager.line_art_seq_items = bpy.props.CollectionProperty(
        type=lr_seq_items
    )
    bpy.types.WindowManager.line_art_target_object = bpy.props.PointerProperty(
        name="Object",
        description="Select Line Art Target Object",
        type=bpy.types.Object,
    )
    bpy.types.WindowManager.line_art_target_collection = bpy.props.PointerProperty(
        name="Collection",
        description="Select Line Art Target Collection",
        type=bpy.types.Collection,
    )
    bpy.types.WindowManager.edit_scene = bpy.props.PointerProperty(
        name="Edit Scene",
        description="Scene that contains Edit Sequence",
        type=bpy.types.Scene,
    )
    bpy.types.Object.line_art_seq_obj = bpy.props.BoolProperty(
        name="Enable Seq Line Art Control",
        description="Control Line Art Object from Sequence",
        default=False,
    )
    bpy.types.Object.line_art_tools_obj = bpy.props.BoolProperty(
        name="Enable Line Art Tools",
        description="TODO",
        default=False,
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.line_art_seq_obj
    del bpy.types.WindowManager.line_art_seq_items
