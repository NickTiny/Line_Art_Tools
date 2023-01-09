from .pro import (
    sync_line_art_obj_to_strip,
    check_anim_is_constant,
)
from .core import (
    line_art_tools_item_add,
    line_art_tools_remove,
    line_art_tools_refresh,
    get_line_art_tools_collection,
)


import bpy


class LINE_ART_TOOLS_OT_base_class(bpy.types.Operator):
    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.mode == "OBJECT"


class LINE_ART_TOOLS_OT_obj_enable(bpy.types.Operator):
    bl_idname = "linearttools.obj_enable"
    bl_label = "Enable Line Art Tools"
    bl_description = "TODO"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.active_object.type == "GPENCIL"
            and not context.active_object.line_art_tools_obj
        )

    def execute(self, context):
        line_art_tools = context.window_manager.line_art_tools_items
        line_art_tools_refresh(line_art_tools)
        line_art_tools_item_add(line_art_tools, context.active_object)
        return {"FINISHED"}


class LINE_ART_TOOLS_OT_obj_disable(bpy.types.Operator):
    bl_idname = "linearttools.obj_disable"
    bl_label = "Disable Line Art Tools"
    bl_description = "TODO"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context):

        return (
            context.active_object.type == "GPENCIL"
            and context.active_object.line_art_tools_obj
        )

    def execute(self, context):
        line_art_tools_items = context.window_manager.line_art_tools_items
        line_art_tools_remove(line_art_tools_items, context.active_object)
        return {"FINISHED"}


class LINE_ART_TOOLS_OT_bake_line_art(LINE_ART_TOOLS_OT_base_class):
    bl_idname = "linearttools.refresh"
    bl_label = "Bake All Line Art"
    bl_description = "TODO"
    bl_options = {"UNDO"}

    def execute(self, context):
        line_art_tools_items = context.window_manager.line_art_tools_items
        context.view_layer.objects.active = line_art_tools_items[0].object
        bpy.ops.object.lineart_clear_all()
        bpy.ops.object.lineart_bake_strokes_all()
        return {"FINISHED"}


class LINE_ART_TOOLS_OT_refresh(bpy.types.Operator):
    bl_idname = "linearttools.refresh"
    bl_label = "Refresh Line Art Tool Items"
    bl_description = "TODO"
    bl_options = {"UNDO"}

    def execute(self, context):
        line_art_tools_items = context.window_manager.line_art_tools_items
        line_art_tools_refresh(line_art_tools_items)
        return {"FINISHED"}


class LINE_ART_TOOLS_OT_obj_select(LINE_ART_TOOLS_OT_base_class):
    bl_idname = "linearttools.obj_select"
    bl_label = "Open Properties Panel for Line Art"
    bl_description = "TODO"
    bl_options = {"UNDO"}

    index: bpy.props.IntProperty(name="index", default=0)

    def execute(self, context):
        line_art_tools_items = context.window_manager.line_art_tools_items
        context.view_layer.objects.active = line_art_tools_items[self.index].object
        for obj in context.selected_objects:
            obj.select_set(False)
        # context.selected_objects.clear()
        line_art_tools_items[self.index].object.select_set(True)
        return {"FINISHED"}


class LINE_ART_TOOLS_OT_copy_mod(LINE_ART_TOOLS_OT_base_class):
    bl_idname = "linearttools.copy_mod"
    bl_label = "Update All Objects"
    bl_description = "Copy Object Settings to all Line Art Modifiers"
    bl_options = {"UNDO"}

    index: bpy.props.IntProperty(name="index", default=0)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        col = self.layout.column(align=False)
        col.label(
            text=f"Copy '{context.window_manager.line_art_tools_items[self.index].object.name}' settings to all Line Art Modifiers?"
        )

    def execute(self, context):

        line_art_tools_items = context.window_manager.line_art_tools_items

        mSrc = line_art_tools_items[self.index].object.grease_pencil_modifiers[
            line_art_tools_items[1].lr_mod
        ]

        # collect names of writable properties
        properties = [
            p.identifier
            for p in mSrc.bl_rna.properties
            if not p.is_readonly
            and p.identifier != "source_object"
            and p.identifier != "target_layer"
            and p.identifier != "target_material"
        ]

        for i, item in enumerate(line_art_tools_items):
            mDst = item.object.grease_pencil_modifiers[line_art_tools_items[i].lr_mod]
            # copy those properties
            for prop in properties:
                setattr(mDst, prop, getattr(mSrc, prop))

        return {"FINISHED"}


class LINE_ART_TOOLS_OT_open_properties(LINE_ART_TOOLS_OT_base_class):
    bl_idname = "linearttools.open_properties"
    bl_label = "Open Properties Panel for Line Art"
    bl_description = "TODO"
    bl_options = {"UNDO"}

    index: bpy.props.IntProperty(name="index", default=0)

    def execute(self, context):
        line_art_tools_items = context.window_manager.line_art_tools_items
        context.view_layer.objects.active = line_art_tools_items[self.index].object
        for obj in context.selected_objects:
            obj.select_set(False)
        line_art_tools_items[self.index].object.select_set(True)

        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)
        for area in context.window.screen.areas:
            if area.type == "PROPERTIES":
                area.spaces[0].context = "MODIFIER"
                return {"FINISHED"}
        self.report({"ERROR"}, "No Properties Editor Found")
        return {"CANCELLED"}


class LINE_ART_TOOLS_OT_stroke_thickness_space(LINE_ART_TOOLS_OT_base_class):
    bl_idname = "linearttools.stroke_thickness_space"
    bl_label = "Reset All Stroke Thickness Spaces"
    bl_description = "TODO"
    bl_options = {"UNDO"}

    def spaces(self, context):
        world = (
            "WORLDSPACE",
            "World",
            "Set all to World Space",
            "WORLD",
            1,
        )
        screen = (
            "SCREENSPACE",
            "Screen",
            "Set all to Screen Space",
            "RESTRICT_VIEW_ON",
            2,
        )
        return world, screen

    space: bpy.props.EnumProperty(name="Space", items=spaces, default=1)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        col = self.layout.column(align=False)
        # col.label(text="Line Art Thickness will reset to defaults", icon="ERROR")
        col.prop(self, "space")

    def execute(self, context):
        line_art_tools_items = context.window_manager.line_art_tools_items
        for item in line_art_tools_items:
            item.object.data.stroke_thickness_space = self.space
        return {"FINISHED"}


class LINE_ART_TOOLS_OT_add_gp(LINE_ART_TOOLS_OT_base_class):
    bl_idname = "linearttools.add_gp"
    bl_label = "Create Line Art Tool Items"
    bl_description = "TODO"
    bl_options = {"UNDO"}

    def enum_items(self, context):
        scene = (
            "LRT_SCENE",
            "Scene",
            "",
            "SCENE_DATA",
            1,
        )
        collection = (
            "LRT_COLLECTION",
            "Collection",
            "",
            "OUTLINER_COLLECTION",
            2,
        )
        object = (
            "LRT_OBJECT",
            "Object",
            "",
            "OBJECT_DATAMODE",
            3,
        )
        return scene, collection, object

    type: bpy.props.EnumProperty(name="Type", items=enum_items, default=1)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        col = self.layout.column(align=False)
        col.prop(self, "type")
        if self.type == "LRT_OBJECT":
            col.prop(context.window_manager, "line_art_target_object")

        if self.type == "LRT_COLLECTION":
            col.prop(context.window_manager, "line_art_target_collection")

    def execute(self, context):
        line_art_tools_items = context.window_manager.line_art_tools_items
        bpy.ops.object.gpencil_add(type=self.type)
        item = line_art_tools_item_add(line_art_tools_items, context.active_object)
        obj = item.object
        obj.name = f"LAT_{context.scene.name}"
        if self.type == "LRT_OBJECT":
            obj.grease_pencil_modifiers[
                item.lr_mod
            ].source_object = context.window_manager.line_art_target_object
            obj.name = f"LAT_{context.window_manager.line_art_target_object.name}"

        if self.type == "LRT_COLLECTION":
            obj.grease_pencil_modifiers[
                item.lr_mod
            ].source_collection = context.window_manager.line_art_target_collection
            obj.name = f"LAT_{context.window_manager.line_art_target_collection.name}"
        obj.users_collection[0].objects.unlink(obj)
        col = get_line_art_tools_collection(context)
        col.objects.link(obj)
        return {"FINISHED"}


class LINE_ART_TOOLS_OT_remove_gp(LINE_ART_TOOLS_OT_base_class):
    bl_idname = "linearttools.remove_gp"
    bl_label = "Delete Object"
    bl_description = "TODO"
    bl_options = {"UNDO"}

    index: bpy.props.IntProperty(name="index", default=0)

    def execute(self, context):
        line_art_tools_items = context.window_manager.line_art_tools_items
        bpy.data.objects.remove(line_art_tools_items[self.index].object)
        line_art_tools_items.remove(self.index)

        return {"FINISHED"}


############################################################################


class SEQUENCER_OT_add_line_art_obj(bpy.types.Operator):
    bl_idname = "view3d.add_line_art_obj"
    bl_label = "Enable Sequence Line Art on Active Object"
    bl_description = "Add Active Grese Pencil Object to Sequence Line Art Items"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.active_object
            and context.active_object.type == "GPENCIL"
            and not context.active_object.line_art_seq_obj
        )

    def execute(self, context):
        obj = context.active_object
        if obj.constraints:
            self.report({"ERROR"}, "Cannot set Line Art if any constraints are present")
            return {"CANCELLED"}
        if any(
            [mod for mod in obj.grease_pencil_modifiers if mod.type == "GP_LINEART"]
        ):
            self.report(
                {"ERROR"}, "Cannot set Line Art if object already has modifiers"
            )
            return {"CANCELLED"}
        line_art_items = context.window_manager.line_art_seq_items
        line_art_mod = obj.grease_pencil_modifiers.new(
            name="Line Art", type="GP_LINEART"
        )
        line_art_mod.name = "SEQ_LINE_ART"
        line_art_mod.target_layer = obj.data.layers[0].info
        line_art_mod.target_material = obj.data.materials[0]
        line_art_mod.source_type = "SCENE"
        add_line_art_item = line_art_items.add()
        add_line_art_item.object = obj

        for strip in context.scene.sequence_editor.sequences_all:
            line_art_mod.keyframe_insert("thickness", frame=strip.frame_final_start)

        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = "CONSTANT"

        obj.line_art_seq_obj = True
        self.report({"INFO"}, f"Added '{obj.name}' to Sequence_Line Art Items")
        return {"FINISHED"}


class SEQUENCER_OT_remove_line_art_obj(bpy.types.Operator):
    bl_idname = "view3d.remove_line_art_obj"
    bl_label = "Disable Sequence Line Art for Active Object"
    bl_description = "Remove Active Grese Pencil Object from Sequence Line Art Items"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.active_object
            and context.active_object.type == "GPENCIL"
            and context.active_object.line_art_seq_obj
        )

    def execute(self, context):
        obj = context.active_object
        # Remove from list of line_art_items
        for item in context.window_manager.line_art_seq_items:
            line_art_items = context.window_manager.line_art_seq_items
        for index, item in enumerate(context.window_manager.line_art_seq_items):
            if item.object == obj:
                line_art_items.remove(index)
        for mod in obj.grease_pencil_modifiers:
            if mod.type == "GP_LINEART":
                obj.grease_pencil_modifiers.remove(mod)
        self.report({"INFO"}, f"Removed '{obj.name}' from Sequence_Line Art Items")
        obj.line_art_seq_obj = False
        return {"FINISHED"}


class SEQUENCER_OT_refresh_line_art_obj(bpy.types.Operator):
    bl_idname = "view3d.refresh_line_art_obj"
    bl_label = "Refresh Sequence Line Art Items"
    bl_description = "Check active strip's scene for avaliable Line Art Objects, and add them to Sequence Line Art Items"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        strip = context.active_sequence_strip
        if not strip or strip.type != "SCENE":
            self.report({"ERROR"}, "There is no active scene strip")
            return {"CANCELLED"}

        line_art_items = context.window_manager.line_art_seq_items
        line_art_items.clear()
        for obj in strip.scene.objects:
            if obj.line_art_seq_obj:
                add_line_art_item = line_art_items.add()
                add_line_art_item.object = obj
                if context.window_manager.line_art_cam_override:
                    obj.grease_pencil_modifiers[
                        "SEQ_LINE_ART"
                    ].source_camera = bpy.data.objects[
                        f"{context.scene.line_art_cam_name}"
                    ]

        self.report({"INFO"}, "'Sequences Line Art Items' Refreshed")
        return {"FINISHED"}


class SEQUENCER_OT_update_similar_strip_line_art(bpy.types.Operator):
    bl_idname = "view3d.update_similar_strip_line_art"
    bl_label = "Copy Line Art to Similar Strips"
    bl_description = (
        "If strip in Sequence Editor uses to active strip; copy all line art values"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        success_msg = ""
        scene = context.scene
        active_strip = scene.sequence_editor.active_strip

        thickness_values = []
        cam_name = active_strip.scene_camera.name

        for item in context.window_manager.line_art_seq_items:
            thickness_values.append(item.thickness)

        strips = [
            strip
            for strip in context.scene.sequence_editor.sequences_all
            if (
                strip.type == "SCENE"
                and strip.name != active_strip.name
                and strip.scene_camera.name == cam_name
            )
        ]
        if not any(strips):
            self.report({"ERROR"}, "No strips share a camera with active strip")
            return {"CANCELLED"}

        for strip in strips:
            scene.frame_set(strip.frame_final_start)
            scene.sequence_editor.active_strip = strip
            for index, item in enumerate(context.window_manager.line_art_seq_items):
                item.thickness = thickness_values[index]
                success_msg = (
                    f"Thickness set to '{item.thickness}' on '{strip.name}' \n"
                )

        self.report({"INFO"}, f"All Similar strips Updated \n {success_msg}")
        return {"FINISHED"}


class SEQUENCER_OT_check_line_art_obj(bpy.types.Operator):
    bl_idname = "view3d.check_line_art_obj"
    bl_label = "Check Line Art Items for Errors"
    bl_description = "Check Sequence Line Art Items are in sync with sequence strips, report any errors if found"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        error_msg = ""
        for item in context.window_manager.line_art_seq_items:
            obj = item.object
            constant_anim = check_anim_is_constant(obj)
            if constant_anim:
                for strip in context.scene.sequence_editor.sequences_all:
                    if strip.type == "SCENE":
                        if not sync_line_art_obj_to_strip(obj, strip):
                            error_msg += f"Object: '{obj.name}' unexpected keyframes within Frame Range: ({strip.frame_final_start}-{strip.frame_final_end}) \n"
            if not constant_anim:
                error_msg += f"UNKOWN ERROR in Object: '{obj.name}' usually caused by wrong interpolation type or missing keyframe error \n"
        if error_msg != "":
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}
        self.report({"INFO"}, "'Sequences Line Art Items' reported no errors")
        return {"FINISHED"}


classes = (
    SEQUENCER_OT_add_line_art_obj,
    SEQUENCER_OT_remove_line_art_obj,
    SEQUENCER_OT_refresh_line_art_obj,
    SEQUENCER_OT_check_line_art_obj,
    SEQUENCER_OT_update_similar_strip_line_art,
    LINE_ART_TOOLS_OT_obj_enable,
    LINE_ART_TOOLS_OT_obj_disable,
    LINE_ART_TOOLS_OT_refresh,
    LINE_ART_TOOLS_OT_add_gp,
    LINE_ART_TOOLS_OT_stroke_thickness_space,
    LINE_ART_TOOLS_OT_open_properties,
    LINE_ART_TOOLS_OT_obj_select,
    LINE_ART_TOOLS_OT_copy_mod,
    LINE_ART_TOOLS_OT_remove_gp,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
