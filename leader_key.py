import json
import os
from time import time
import bpy

# All of the events that can be used when writing Key String for bindings.
_EVENTS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
          'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'ZERO',
          'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT',
          'NINE', 'LEFT_CTRL', 'LEFT_ALT', 'LEFT_SHIFT', 'RIGHT_ALT',
          'RIGHT_CTRL', 'RIGHT_SHIFT', 'OSKEY', 'GRLESS', 'ESC', 'TAB', 'RET',
          'SPACE', 'LINE_FEED', 'BACK_SPACE', 'DEL', 'SEMI_COLON', 'PERIOD',
          'COMMA', 'QUOTE', 'ACCENT_GRAVE', 'MINUS', 'SLASH', 'BACK_SLASH',
          'EQUAL', 'LEFT_BRACKET', 'RIGHT_BRACKET', 'LEFT_ARROW', 'DOWN_ARROW',
          'RIGHT_ARROW', 'UP_ARROW', 'NUMPAD_2', 'NUMPAD_4', 'NUMPAD_6',
          'NUMPAD_8', 'NUMPAD_1', 'NUMPAD_3', 'NUMPAD_5', 'NUMPAD_7',
          'NUMPAD_9', 'NUMPAD_PERIOD', 'NUMPAD_SLASH', 'NUMPAD_ASTERIX',
          'NUMPAD_0', 'NUMPAD_MINUS', 'NUMPAD_ENTER', 'NUMPAD_PLUS', 'F1',
          'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
          'F13', 'F14', 'F15', 'F16', 'F17', 'F18', 'F19', 'PAUSE', 'INSERT',
          'HOME', 'PAGE_UP', 'PAGE_DOWN', 'END', 'MEDIA_PLAY', 'MEDIA_STOP',
          'MEDIA_FIRST', 'MEDIA_LAST', 'TEXTINPUT', 'WINDOW_DEACTIVATE',
          'TIMER', 'TIMER0', 'TIMER1', 'TIMER2', 'TIMER_JOBS',
          'TIMER_AUTOSAVE', 'TIMER_REPORT', 'TIMERREGION', 'NDOF_MOTION',
          'NDOF_BUTTON_MENU', 'NDOF_BUTTON_FIT', 'NDOF_BUTTON_TOP',
          'NDOF_BUTTON_BOTTOM', 'NDOF_BUTTON_LEFT', 'NDOF_BUTTON_RIGHT',
          'NDOF_BUTTON_FRONT', 'NDOF_BUTTON_BACK', 'NDOF_BUTTON_ISO1',
          'NDOF_BUTTON_ISO2', 'NDOF_BUTTON_ROLL_CW', 'NDOF_BUTTON_ROLL_CCW',
          'NDOF_BUTTON_SPIN_CW', 'NDOF_BUTTON_SPIN_CCW', 'NDOF_BUTTON_TILT_CW',
          'NDOF_BUTTON_TILT_CCW', 'NDOF_BUTTON_ROTATE', 'NDOF_BUTTON_PANZOOM',
          'NDOF_BUTTON_DOMINANT', 'NDOF_BUTTON_PLUS', 'NDOF_BUTTON_MINUS',
          'NDOF_BUTTON_ESC', 'NDOF_BUTTON_ALT', 'NDOF_BUTTON_SHIFT',
          'NDOF_BUTTON_CTRL', 'NDOF_BUTTON_1', 'NDOF_BUTTON_2',
          'NDOF_BUTTON_3', 'NDOF_BUTTON_4', 'NDOF_BUTTON_5', 'NDOF_BUTTON_6',
          'NDOF_BUTTON_7', 'NDOF_BUTTON_8', 'NDOF_BUTTON_9', 'NDOF_BUTTON_10',
          'NDOF_BUTTON_A', 'NDOF_BUTTON_B', 'NDOF_BUTTON_C']

# Drop events that no longer exist in the running version of blender.
_VALID_EVENTS = {item.identifier for item in
                 bpy.types.Event.bl_rna.properties['type'].enum_items}
EVENTS = [e for e in _EVENTS if e in _VALID_EVENTS]


def _rna_enum(struct, prop):
    """Build EnumProperty items from blender's own enum, plus 'All'."""
    items = [(item.identifier, item.identifier, '')
             for item in struct.bl_rna.properties[prop].enum_items]
    return items + [('All', 'All', '')]


CTYPE_ENUM = _rna_enum(bpy.types.Area, 'type')
CMODE_ENUM = _rna_enum(bpy.types.Context, 'mode')

KEYSTR_DESC = ('String of characters to be used as key binding. For ex: '
               '"A B C" would mean that after pressing leader key pressing'
               ' in A, B, C keys in sequence would lead to calling bound '
               'function. You can use all the keys that blender outputs in '
               'event.type, except mouse movement:\n{}'
              ).format(' '.join(EVENTS))
FUNC_DESC = 'Function to be used by this key binding.'
CTYPE_DESC = 'Type of area in which this key binding is to be used in.'
CMODE_DESC = 'Mode in which this key binding is to be used in.'


class LeaderKey(bpy.types.Operator):
    """Main function call"""
    bl_idname = 'ui.leaderkey'
    bl_label = 'Launch leader key'

    # Timer from blender so modal method updates on 'TIMER' events
    _timer = None
    key_string = ''
    timeout = 0
    timenext = 0
    timestart = 0
    bindings = None

    def execute(self, context):
        return self.invoke(context, None)

    def invoke(self, context, event):
        addon_prefs = context.preferences.addons[__package__].preferences
        self.key_string = ''
        self.timeout = addon_prefs.timeout
        self.timenext = addon_prefs.time_for_next
        self.bindings = Bindings()
        for b in addon_prefs.bindings:
            self.bindings.append(b.kstr, b.func, b.ctype, b.cmode)
        self.timestart = time()
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.001, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finish(self, context):
        context.window_manager.event_timer_remove(self._timer)
        if context.area:
            context.area.header_text_set(None)

    def modal(self, context, event):
        if event.type == 'ESC':
            self.finish(context)
            return {'CANCELLED'}
        if event.type in EVENTS and event.value == 'PRESS':
            self.key_string += event.type + ' '

        area_type = context.area.type if context.area else 'All'

        # Go through possible functions trying different contexts.
        # Try first with current context and then try to find functions
        # that are correct for all contexts.
        func = self.bindings.get(kstr=self.key_string,
                                 ctype=area_type,
                                 cmode=context.mode)
        if not func:
            func = self.bindings.get(kstr=self.key_string,
                                     ctype='All',
                                     cmode=context.mode)
        if not func:
            func = self.bindings.get(kstr=self.key_string,
                                     ctype=area_type,
                                     cmode='All')
        if not func:
            func = self.bindings.get(kstr=self.key_string,
                                     ctype='All',
                                     cmode='All')

        if context.area:
            context.area.header_text_set(self.key_string)

        if func and (time() - self.timestart) >= self.timenext:
            self.finish(context)
            exec(func)
            return {'FINISHED'}

        if (time() - self.timestart) >= self.timeout:
            self.finish(context)
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


class Bindings:
    """Class containing all the bindings."""

    def __init__(self):
        self._bindings = {}

    def append(self,
               kstr,
               func,
               ctype='All',
               cmode='All'):
        """
        Append binding for key combination string 'kstr' and bind it with
        function 'func'.
        Constrain that binding to context_area_type 'ctype' and context_mode
        'cmode'
        """
        # Blenders event.type has all the keys in upper case.
        kstr = kstr.upper().strip()
        self._bindings.setdefault(ctype, {}).setdefault(cmode, {})[kstr] = func

    def get(self, kstr, ctype='All', cmode='All'):
        """
        Get function for key_string 'kstr' bound by context type and mode:
        'ctype', 'cmode'
        """
        try:
            return self._bindings[ctype][cmode][kstr.upper().strip()]
        except KeyError:
            return None


CONFIG_FILE = 'bindings.json'
BINDING_PROPS = ('kstr', 'func', 'ctype', 'cmode')
SETTING_PROPS = ('timeout', 'time_for_next')

# Set while restoring from file so property updates don't write it back
_loading = False

def _config_path():
    try:
        directory = bpy.utils.extension_path_user(__package__, create=True)
    except ValueError:
        # legacy add-on
        directory = bpy.utils.user_resource('CONFIG', path='leader_key',
                                            create=True)
    return os.path.join(directory, CONFIG_FILE)


def _get_prefs(context=None):
    context = context or bpy.context
    addon = context.preferences.addons.get(__package__)
    return addon.preferences if addon else None


def save_bindings(context=None):
    prefs = _get_prefs(context)
    if _loading or prefs is None:
        return
    data = {name: getattr(prefs, name) for name in SETTING_PROPS}
    data['bindings'] = [{name: getattr(b, name) for name in BINDING_PROPS}
                        for b in prefs.bindings]
    with open(_config_path(), 'w') as f:
        json.dump(data, f, indent=2)


def load_bindings(context=None):
    """
    Restore preferences from file. If there's no file yet, write current
    preferences to it instead, so nothing set before is lost.
    """
    global _loading
    prefs = _get_prefs(context)
    if prefs is None:
        return
    path = _config_path()
    if not os.path.exists(path):
        save_bindings(context)
        return
    try:
        with open(path) as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        print('Leader Key: could not read {}: {}'.format(path, e))
        return
    _loading = True
    try:
        for name in SETTING_PROPS:
            if name in data:
                setattr(prefs, name, data[name])
        prefs.bindings.clear()
        for entry in data.get('bindings', []):
            binding = prefs.bindings.add()
            for name in BINDING_PROPS:
                if name not in entry:
                    continue
                try:
                    setattr(binding, name, entry[name])
                except TypeError:
                    # Area type or mode not present in this blender version
                    pass
    finally:
        _loading = False


def _on_update(self, context):
    save_bindings(context)


class LeaderKeyBinding(bpy.types.PropertyGroup):
    kstr: bpy.props.StringProperty(name="Key String",
                                   description=KEYSTR_DESC,
                                   update=_on_update)
    func: bpy.props.StringProperty(name="Function",
                                   description=FUNC_DESC,
                                   update=_on_update)
    ctype: bpy.props.EnumProperty(items=CTYPE_ENUM,
                                  name="Context area type",
                                  description=CTYPE_DESC,
                                  default="All",
                                  update=_on_update)
    cmode: bpy.props.EnumProperty(items=CMODE_ENUM,
                                  name="Context mode",
                                  description=CMODE_DESC,
                                  default="All",
                                  update=_on_update)


class LeaderKeyBindingAdd(bpy.types.Operator):
    """Add new leader key binding"""
    bl_idname = 'ui.leaderkey_binding_add'
    bl_label = 'Add Binding'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.bindings.add()
        context.preferences.is_dirty = True
        save_bindings(context)
        return {'FINISHED'}


class LeaderKeyBindingRemove(bpy.types.Operator):
    """Remove leader key binding"""
    bl_idname = 'ui.leaderkey_binding_remove'
    bl_label = 'Remove Binding'
    bl_options = {'INTERNAL'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.bindings.remove(self.index)
        context.preferences.is_dirty = True
        save_bindings(context)
        return {'FINISHED'}


# Blender requires dynamic enum items to stay referenced from python, so
# keep them at module level. Refreshed every time search popup is opened so
# operators from newly enabled add-ons show up too.
_operator_items = []


def _refresh_operators():
    _operator_items.clear()
    for module_name in dir(bpy.ops):
        module = getattr(bpy.ops, module_name)
        for op_name in dir(module):
            idname = '{}.{}'.format(module_name, op_name)
            try:
                rna = getattr(module, op_name).get_rna_type()
            except (AttributeError, KeyError, RuntimeError):
                continue
            label = rna.name or op_name
            _operator_items.append(
                (idname, '{} ({})'.format(label, idname), rna.description))
    _operator_items.sort(key=lambda item: item[1].lower())


def _operator_enum(self, context):
    return _operator_items


class LeaderKeyBindingSearch(bpy.types.Operator):
    """Search for an operator to use as this binding's function"""
    bl_idname = 'ui.leaderkey_binding_search'
    bl_label = 'Search Operator'
    bl_options = {'INTERNAL'}
    bl_property = 'operator'

    index: bpy.props.IntProperty()
    operator: bpy.props.EnumProperty(items=_operator_enum)

    def invoke(self, context, event):
        _refresh_operators()
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.bindings[self.index].func = 'bpy.ops.{}()'.format(self.operator)
        context.preferences.is_dirty = True
        return {'FINISHED'}


class LeaderKeyPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    timeout: bpy.props.FloatProperty(
        name="Timeout",
        description="Amount of time for typing keys. In seconds.",
        default=1.0,
        soft_min=0.01,
        update=_on_update)

    time_for_next: bpy.props.FloatProperty(
        name="Wait for next",
        description=("Amount of time for which to wait for next key if "
                     "matching key is already found. In seconds."),
        default=0.5,
        soft_min=0.01,
        update=_on_update)

    bindings: bpy.props.CollectionProperty(type=LeaderKeyBinding)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "timeout")
        layout.prop(self, "time_for_next")
        for i, binding in enumerate(self.bindings):
            box = layout.box()
            row = box.row()
            row.label(text="Binding {}".format(i))
            row.operator(LeaderKeyBindingRemove.bl_idname, text="",
                         icon='X', emboss=False).index = i
            box.prop(binding, "kstr")
            row = box.row(align=True)
            row.prop(binding, "func")
            row.operator(LeaderKeyBindingSearch.bl_idname, text="",
                         icon='VIEWZOOM').index = i
            row = box.row()
            row.prop(binding, "ctype")
            row.prop(binding, "cmode")
        layout.operator(LeaderKeyBindingAdd.bl_idname, icon='ADD')


classes = (
    LeaderKey,
    LeaderKeyBinding,
    LeaderKeyBindingAdd,
    LeaderKeyBindingRemove,
    LeaderKeyBindingSearch,
    LeaderKeyPreferences,
)
