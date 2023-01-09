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
                text="Global Thickness",
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
        # col.prop(context.window_manager, "edit_scene")


class VIEW3D_sequence_line_art_panel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
    bl_idname = "VIEW3D_PT_sequencer_line_art"
    bl_label = "Line Art Tools"

    def draw(self, context):
        row = self.layout.row(align=True)
        row.label(text="Sequence Line Art")
        row.operator("linearttools.obj_enable", icon="MOD_LINEART", text="Enable")
        row.operator("linearttools.obj_disable", icon="X", text="Disable")


classes = (
    VIEW3D_sequence_line_art_panel,
    LINE_ART_TOOLS_PT_control,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
