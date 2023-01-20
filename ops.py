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


classes = (
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
