import bpy

from . import leader_key


bl_info = {
    'name'        : 'Leader Key',
    'location'    : ('Add shortcut to ui.leaderkey '
                     'or access through search menu.'),
    'description' : 'Vim like <leader> key functionality for blender',
    'author'      : 'Adam Wolski(miniukof@gmail.com)',
    'doc_url'     : 'https://github.com/miniukof/bl-leader_key',
    'version'     : (0, 1, 0),
    'blender'     : (4, 2, 0),
    'category'    : 'User Interface',
}


def register():
    for cls in leader_key.classes:
        bpy.utils.register_class(cls)
    leader_key.load_bindings()

def unregister():
    for cls in reversed(leader_key.classes):
        bpy.utils.unregister_class(cls)
