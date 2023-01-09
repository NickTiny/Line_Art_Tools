from . import ops, props, ui, pro  # line_art_cam

bl_info = {
    "name": "Line Art Tools",
    "author": "Nick Alberelli",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}


def register():
    ops.register()
    props.register()
    ui.register()
    pro.register()


def unregister():
    ops.unregister()
    props.unregister()
    ui.unregister()
    pro.unregister()
