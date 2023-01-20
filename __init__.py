from . import ops, props, ui

bl_info = {
    "name": "Line Art Tools",
    "author": "Nick Alberelli",
    "description": "Line Art tools is a tool to quickly and easily control the thickness of multiple Line Art Objects at once. Line Art tools gives editing, copy settings and global thickness offset options to user.",
    "blender": (3, 3, 0),
    "version": (1, 0, 0),
    "location": "3D View > Sidebar > Line Art Tools",
    "warning": "",
    "category": "Object",
}


def register():
    ops.register()
    props.register()
    ui.register()


def unregister():
    ops.unregister()
    props.unregister()
    ui.unregister()
