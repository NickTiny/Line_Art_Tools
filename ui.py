import bpy


class LINE_ART_TOOLS_PT_control(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "LINE_ART_TOOLS_PT_control"
    bl_label = "Line Art Tools"
    bl_category = "Line Art Tools"

    def draw(self, context):
        line_art_tools_items = context.window_manager.line_art_tools_items
        if len(line_art_tools_items) < 0:
            return

        layout = self.layout
        col = layout.box()
        row = col.row(align=False)
        if len(line_art_tools_items) >= 1:
            row.prop(
                line_art_tools_items[0],
                "thickness_offset",
                slider=False,
                expand=False,
                text="Thickness Offset",
            )
        row.operator("linearttools.refresh", icon="FILE_REFRESH", text="")
        row.operator(
            "linearttools.stroke_thickness_space", icon="MOD_THICKNESS", text=""
        )

        row.operator("linearttools.add_gp", icon="PLUS", text="")

        for index, item in enumerate(line_art_tools_items):
            box = col.box()
            row = box.row(align=False)

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

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=False)
        row = col.row(align=True)
        row.prop(context.window_manager, "line_art_cam_override", text="")
        row.label(text="Override Line Art Camera", icon="CAMERA_DATA")
        row = col.row(align=True)
        col = layout.box()
        row = col.row(align=False)
        row.label(text="Sequence Line Art Items", icon="MOD_LINEART")
        row.operator("view3d.check_line_art_obj", icon="ERROR", text="Check Line Art")
        row.operator("view3d.update_similar_strip_line_art", icon="DUPLICATE", text="")
        row.operator("view3d.refresh_line_art_obj", icon="FILE_REFRESH", text="")

        if context.active_sequence_strip is None:
            return
        for item in context.window_manager.line_art_seq_items:
            if len(item.object.users_scene) != 0:
                box = col.box()
                row = box.row(align=True)
                if item.status == False:
                    row.alert = True
                row.prop(
                    item, "thickness", slider=False, expand=False, text=item.object.name
                )
                row.prop(
                    item,
                    "viewport",
                    slider=False,
                    expand=False,
                    text="",
                    icon="RESTRICT_VIEW_OFF",
                )


class VIEW3D_sequence_line_art_panel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
    bl_idname = "VIEW3D_PT_sequencer_line_art"
    bl_label = "Line Art Tools"

    def draw(self, context):
        row = self.layout.row(align=True)
        row.label(text="Sequence Line Art")
        # row.operator("view3d.add_line_art_obj", icon="MOD_LINEART", text="Enable")
        # row.operator("view3d.remove_line_art_obj", icon="X", text="Disable")
        row.operator("linearttools.obj_enable", icon="MOD_LINEART", text="Enable")
        row.operator("linearttools.obj_disable", icon="X", text="Disable")


classes = (
    SEQUENCER_PT_line_art,
    VIEW3D_sequence_line_art_panel,
    LINE_ART_TOOLS_PT_control,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
