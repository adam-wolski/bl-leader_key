# Vim like 'leader' key functionality for blender.

![alt text](http://i.imgur.com/eppBtCH.gif "Example")

In my workflow I use a lot of shortcuts, so much in fact that now I can't really find empty slots for new bindings. So I looked to other software that I love and use a lot of hotkeys in: Vim. In Vim shortcuts can be specified as sequence of keys. For example: 
```vim 
nnoremap <leader>cf :call_function()<CR>
```
Means that after pressing `leader` key followed by `c` and `f` keys call `call_function()`. Reading sequence of characters as shortcut means that we get a lot of new possible shortcuts without having to stretch our hands all-over the keyboard. 

Thats the functionality I tried to replicate in this add-on.

# Installation

Requires Blender 4.2 or newer.

Download repository as zip file.
In Preferences window go to the Get Extensions (or Add-ons) tab, open the drop-down menu in the top right corner, select "Install from Disk..." and point it to the add-on zip.

# Configuration

## Leading Key (add-on key-binding)

I personally am not a fan of add-ons that register keyboard shortcuts by themselves. I leave that for the user. Function call for starting add-on is `ui.leaderkey`.

To add shortcut in blender:

* Go to the Keymap tab in Preferences select context in which that shortcut is to be bound by. In case of this add-on it's best to select something pretty high like Screen so you can call it whether you are in 3D View or Node Editor.

* Go through context options till you get to the "Add New" button. Click it. It will create new shortcut. Type `ui.leaderkey` in the `Identifier of operator to call on input event` field, specify shortcut and you're done.

## Preferences

All the preferences for add-on are available in the Add-ons tab of Preferences window. 
They are also saved to `bindings.json` in the add-on's user directory (`extensions/.user/<repository>/leader_key/` inside Blender's user config).

![alt text](http://i.imgur.com/AVDuwCN.jpg "Add-on Preferences")

* `Add Binding` / `X` - Add a new binding or remove an existing one.

* `Timeout` - Amount of time to wait if no function call was found for typed sequence. (In seconds)

* `Wait For Next` - Amount of time you have to type next key if there's already function call for current sequence. (In seconds)

* `Key String` - Sequence of key events separated by space. Can be almost any of the types in [event.type](https://docs.blender.org/api/current/bpy.types.Event.html#bpy.types.Event.type).

* `Function` - Python function to be executed after sequenced is matched. Can be anything python script could call so you can type either something blender specific like: `bpy.ops.mesh.primitive_torus_add()` or generic python: `print("Hello World")`. Click the magnifying glass next to the field to search all available operators by name.

* `Context area type` - Context area in which to use this binding. Select 'All' to not bind it to any of the specific types of the window.

* `Context mode` - Same as above just for mode of the window.

# Usage

Call the `ui.leaderkey` function and start typing your sequence, after you're done function you specified will be called.

# Tips

Calling some of the blender functions isn't that obvious so here are some tips for common functions you would want to call.

* To call pie menu use `bpy.ops.wm.call_menu_pie(name="pie_menu_name")` where `pie_menu_name` is `bl_idname` of that pie menu so for example `ui.screen_pie_menu`

* To call most other functions start with `bpy.ops.` so for example calling `bpy.types.Operator` function with `bl_idname` of `mesh.some_operation` you would call `bpy.ops.mesh.some_operation()`
