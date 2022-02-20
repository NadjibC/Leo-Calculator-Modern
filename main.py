"""
A Google Calculator Alternative for PC
"""

import os
import sys
from kivy.config import ConfigParser
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import get_color_from_hex

import kivy
from kivymd.app import MDApp
from kivymd.material_resources import DEVICE_TYPE
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, \
    MDRectangleFlatButton as MDRectangleButton, MDIconButton
from kivymd.uix.card import MDSeparator
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem, OneLineAvatarListItem, ImageLeftWidget
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField, MDTextFieldRect
from kivymd.uix.toolbar import MDToolbar

import kivymd

__app__ = 'leo-calc'
__version__ = 0.4
ConfigPath = os.path.expanduser('~/.config/leo_calc_modern.ini')

config = ConfigParser()

if not os.path.exists(ConfigPath):
    open(ConfigPath, 'w', encoding="UTF-8").write('''
[Appearance]
dark = 0
buttons = Default
primary_color = Indigo
accent_color = Red

[Fonts]
font_size = 40
input_font_size = 32
mini_result_font_size = 29

[Behavior]
last_mode = simple
size = (504, 762)
last_dialog = dialog

''')

config.read(ConfigPath)

if DEVICE_TYPE != "mobile":
    Window.hide()
    Window.size = eval(config['Behavior']['size'])

if config['Appearance']['buttons'] == "Raised":
    MDRectangleFlatButton = MDRaisedButton
elif config['Appearance']['buttons'] == "Bordered":
    MDRectangleFlatButton = MDRectangleButton
elif config['Appearance']['buttons'] == "Default":
    MDRectangleFlatButton = MDFlatButton


class Item(OneLineAvatarListItem):
    text = StringProperty()

    def __init__(self, **kwargs):
        super(Item, self).__init__(**kwargs)
        img = ImageLeftWidget()
        img.source = "kivymd/images/" + self.text.lower() + ".png"
        self.add_widget(img)

    def on_release(self, button=None):
        if button == 0:
            config['Behavior']['last_dialog'] = "accent_dialog"
            app.accent_dialog.dismiss()
        elif button == 1:
            config['Behavior']['last_dialog'] = "dialog"
            app.dialog.dismiss()
        elif button == 2:
            config['Behavior']['last_dialog'] = "font_dialog"
            app.font_dialog.dismiss()
        config.write()

        app.refresh_drawer()
        app.set_color_(self)


class minipad_layout(MDGridLayout):
    def __init_fonts__(self):
        for button in self.button_list:
            button.font_size = config['Fonts']['font_size']
            button.text_color = app.toolbar_for_simple.specific_text_color
            button.opposite_colors = True

    @staticmethod
    def back(btn=None):
        if btn:
            pass

        text = app.main_input.text
        cursor = app.main_input.cursor
        if cursor != (0, 0):
            app.main_input.text = (text[:cursor[0] - 1] + text[cursor[0]:])
            app.main_input.cursor = (cursor[0] - 1, cursor[1])
        app.main_input.focus = True

    @staticmethod
    def pm(btn):
        if btn:
            pass
        try:
            app.main_input.text = str(app.numpad.sum(app.main_input.text + ' * -1'))
        except SyntaxError:
            pass

    @staticmethod
    def clear(caller):
        if caller:
            pass

        app.main_input.text = ''
        app.main_input.focus = True

    def __init_colors__(self):
        self.md_bg_color = app.theme_cls.primary_color

    def __init__(self):
        super(minipad_layout, self).__init__()

        self.halign = 'center'
        self.rows = 1
        self.cols = 5
        self.button_list = []
        self.size_hint = (1, None)

        self.button_pm = MDRectangleFlatButton(text='-/+', on_release=self.pm)
        self.button_list.append(self.button_pm)
        self.add_widget(self.button_pm)

        self.button_c = MDRectangleFlatButton(text='C', on_release=self.clear)
        self.button_list.append(self.button_c)
        self.add_widget(self.button_c)

        self.button_start_group = MDRectangleFlatButton(text='(', on_release=numpad_layout().adder)
        self.button_list.append(self.button_start_group)
        self.add_widget(self.button_start_group)

        self.button_end_group = MDRectangleFlatButton(text=')', on_release=numpad_layout().adder)
        self.button_list.append(self.button_end_group)
        self.add_widget(self.button_end_group)

        self.button_back = MDFlatButton(text='<-', on_release=self.back)
        self.button_list.append(self.button_back)
        self.add_widget(self.button_back)

        for button in self.button_list:
            button.size_hint = (1, 1)
            button.line_color = (0, 0, 0, 0)
            button.text_color = app.toolbar_for_simple.specific_text_color

        self.button_back.size_hint = (1, 1)
        self.button_end_group.size_hint = (0.6, 1)
        self.button_start_group.size_hint = (0.6, 1)

        self.__init_fonts__()
        try:
            self.__init_colors__()
        except NameError:
            pass


class numpad_layout(MDGridLayout):
    def __init_fonts__(self):
        for button in self.button_list:
            button.font_size = config['Fonts']['font_size']
        app.main_input.font_size = config['Fonts']['input_font_size']
        self.button_right.user_font_size = int(config['Fonts']['font_size'])
        self.button_left.user_font_size = int(config['Fonts']['font_size'])
        self.button_cp.user_font_size = int(config['Fonts']['font_size'])
        self.button_redo.user_font_size = int(config['Fonts']['font_size'])
        self.button_undo.user_font_size = int(config['Fonts']['font_size'])
        self.__init_colors__()

    def __init_colors__(self):
        self.prelayout_2.md_bg_color = app.theme_cls.primary_color
        for button in self.button_list:
            if (button == self.button_divide
                    or button == self.button_plus
                    or button == self.button_minus
                    or button == self.button_equal
                    or button == self.button_multiply):
                button.text_color = app.toolbar_for_simple.specific_text_color

    def __init__(self):
        """
        Adding buttons to numpad
        """

        super(numpad_layout, self).__init__()

        self.prelayout_1 = MDGridLayout(cols=4)

        self.halign = 'center'
        self.cols = 2
        self.button_list = []
        self.button_divide = MDRectangleFlatButton(text='÷', on_release=self.adder)
        self.button_divide.font_size = self.button_divide.width / 1.5
        self.button_divide.text_color = app.toolbar_for_simple.specific_text_color
        self.button_divide.size_hint = (1, 1)
        self.button_list.append(self.button_divide)

        self.button_multiply = MDRectangleFlatButton(text='×', on_release=self.adder)
        self.button_multiply.text_color = app.toolbar_for_simple.specific_text_color
        self.button_multiply.size_hint = (1, 1)
        self.button_list.append(self.button_multiply)

        self.button_minus = MDRectangleFlatButton(text='-', on_release=self.adder)
        self.button_minus.text_color = app.toolbar_for_simple.specific_text_color
        self.button_minus.size_hint = (1, 1)
        self.button_list.append(self.button_minus)

        self.button_plus = MDRectangleFlatButton(text='+', on_release=self.adder,
                                                 font_size=self.button_divide.width / 2)
        self.button_plus.text_color = app.toolbar_for_simple.specific_text_color
        self.button_list.append(self.button_plus)

        self.button_equal = MDRectangleFlatButton(text='=', on_release=self.adder)
        self.button_equal.font_size = self.button_multiply.width / 1.5
        self.button_equal.text_color = app.toolbar_for_simple.specific_text_color
        self.button_list.append(self.button_equal)

        self.button_dot = MDRectangleFlatButton(text='.', on_release=self.adder)
        self.button_list.append(self.button_dot)
        self.button_0 = MDRectangleFlatButton(text='0', on_release=self.adder)
        self.button_list.append(self.button_0)
        self.button_1 = MDRectangleFlatButton(text='1', on_release=self.adder)
        self.button_list.append(self.button_1)
        self.button_2 = MDRectangleFlatButton(text='2', on_release=self.adder)
        self.button_list.append(self.button_2)
        self.button_3 = MDRectangleFlatButton(text='3', on_release=self.adder)
        self.button_list.append(self.button_3)
        self.button_4 = MDRectangleFlatButton(text='4', on_release=self.adder)
        self.button_list.append(self.button_4)
        self.button_5 = MDRectangleFlatButton(text='5', on_release=self.adder)
        self.button_list.append(self.button_5)
        self.button_6 = MDRectangleFlatButton(text='6', on_release=self.adder)
        self.button_list.append(self.button_6)
        self.button_7 = MDRectangleFlatButton(text='7', on_release=self.adder)
        self.button_list.append(self.button_7)
        self.button_8 = MDRectangleFlatButton(text='8', on_release=self.adder)
        self.button_list.append(self.button_8)
        self.button_9 = MDRectangleFlatButton(text='9', on_release=self.adder)
        self.button_list.append(self.button_9)
        self.button_left = MDIconButton(icon='arrow-left', on_release=self.adder)

        self.button_list.append(self.button_left)
        self.button_right = MDIconButton(icon='arrow-right', on_release=self.adder)

        self.button_list.append(self.button_right)
        self.button_cp = MDIconButton(icon='clipboard-plus', on_release=self.adder)

        self.button_list.append(self.button_cp)
        self.button_redo = MDIconButton(icon='redo', on_release=self.adder)
        self.button_list.append(self.button_redo)
        self.button_undo = MDIconButton(icon="undo", on_release=self.adder)
        self.button_list.append(self.button_undo)

        self.prelayout_1.add_widget(self.button_7)
        self.prelayout_1.add_widget(self.button_8)
        self.prelayout_1.add_widget(self.button_9)
        self.prelayout_1.add_widget(self.button_cp)
        self.prelayout_1.add_widget(self.button_4)
        self.prelayout_1.add_widget(self.button_5)
        self.prelayout_1.add_widget(self.button_6)
        self.prelayout_1.add_widget(self.button_undo)
        self.prelayout_1.add_widget(self.button_1)
        self.prelayout_1.add_widget(self.button_2)
        self.prelayout_1.add_widget(self.button_3)
        self.prelayout_1.add_widget(self.button_redo)
        self.prelayout_1.add_widget(self.button_0)
        self.prelayout_1.add_widget(self.button_dot)
        self.prelayout_1.add_widget(self.button_left)
        self.prelayout_1.add_widget(self.button_right)

        self.prelayout_2 = MDGridLayout(cols=1)
        self.prelayout_2.add_widget(
            self.button_divide)
        self.prelayout_2.add_widget(
            self.button_multiply)
        self.prelayout_2.add_widget(
            self.button_minus)
        self.prelayout_2.add_widget(
            self.button_plus)
        self.prelayout_2.add_widget(
            self.button_equal)
        self.prelayout_2.size_hint = (0.3, 1)

        self.add_widget(self.prelayout_1)
        self.add_widget(self.prelayout_2)

        for button in self.button_list:
            if (MDRectangleFlatButton == MDRaisedButton
                    and button != self.button_divide
                    and button != self.button_plus
                    and button != self.button_minus
                    and button != self.button_equal
                    and button != self.button_multiply):

                if eval(config['Appearance']['dark']):
                    button.text_color = get_color_from_hex('#FFFFFF')
            button.height = self.minimum_height
            button.size_hint = (1, 1)

        self.__init_fonts__()

    @staticmethod
    def sum(arg):
        if arg != "":
            try:
                x = eval(arg.replace('×', '*').replace('÷', '/'))
                if x == int(x):
                    x = int(x)
                return str(x)
            except SyntaxError as err:
                print(err)
            except TypeError as err:
                print(err)

    def refresh(self, line, text):
        app.mini_result.text = ''
        cursor = line.cursor
        try:
            app.main_input.text = app.main_input.text.replace('*', '×').replace('/', '÷')
            app.mini_result.text = self.sum(text)
        except ValueError:
            pass

        line.cursor = cursor
        line.Focus = True

    def adder(self, button):
        cursor = app.main_input.cursor[0] + 1

        if button == self.button_undo:
            x = ''
            app.main_input.do_undo()

        elif button == self.button_redo:
            x = ''
            app.main_input.do_redo()

        elif button == self.button_left:
            x = ''
            cursor -= 2

        elif button == self.button_right:
            x = ''
        elif button == self.button_cp:
            x = ''
            Clipboard.copy(app.main_input.text)
        elif button == self.button_redo:
            x = ''
        elif button == self.button_equal:
            try:
                if not app.main_input.text == '':
                    text = app.main_input.text.replace('÷', '/').replace('x', '*')
                    app.main_input.text = str(self.sum(text))
                    x = ''
                else:
                    x = ''
            except ValueError:
                x = ''
        else:
            x = button.text

        app.main_input.insert_text(str(x))
        app.main_input.cursor = (cursor, 0)
        app.main_input.focus = True

    @staticmethod
    def calculate():
        try:
            app.main_input.text = eval(app.main_input.text)
        except SyntaxError as err:
            app.mini_result.text = str(err)


class App(MDApp):
    last_keys = []
    drawer_items = []
    main_input = None
    numpad = None
    toolbar_for_simple = None
    toolbar_for_scientific = None
    toolbar_for_about = None
    dialog = None
    old_screen = None
    nav_drawer = None
    minpad = None
    mini_result_font_size = None
    input_font_size = None
    mini_result = None
    font_dialog = None
    accent_dialog = None
    lb1 = None
    lb2 = None
    lb3 = None
    screen = None
    screenmgr = None
    font_size = None

    @staticmethod
    def set_text(textfield, text):
        textfield.text = text

    def __init_drawer(self):
        layout = MDBoxLayout(orientation="vertical")
        layout.add_widget(Image(source=self.icon))

        for screen in self.screenmgr.screens:
            item = OneLineListItem(text=screen.name.title(),
                                   on_press=self.set_screen)

            self.drawer_items.append(item)
            layout.add_widget(item)

        self.nav_drawer.add_widget(layout)
        self.refresh_drawer()

    def set_color(self):

        content = MDGridLayout(cols=4)
        self.font_size = MDTextFieldRect(text=config['Fonts']['font_size'], halign="center")
        self.font_size.bind(text=self.on_config_change)
        lb = MDLabel(text="Buttons F. Size")
        btn1 = MDIconButton(icon="minus", size_hint=(1, 1),
                            on_release=lambda x: self.set_text(
                                self.font_size,
                                str(int(self.font_size.text) - 1)
                            ))

        btn2 = MDIconButton(icon="plus", size_hint=(1, 1),
                            on_release=lambda x: self.set_text(
                                self.font_size,
                                str(int(self.font_size.text) + 1)
                            ))

        content.add_widget(lb)
        content.add_widget(btn1)
        content.add_widget(self.font_size)
        content.add_widget(btn2)
        content.add_widget(MDSeparator())
        content.add_widget(MDSeparator())
        content.add_widget(MDSeparator())
        content.add_widget(MDSeparator())

        self.input_font_size = MDTextFieldRect(text=config['Fonts']['input_font_size'], halign="center")
        self.input_font_size.bind(text=self.on_config_change)
        lb2 = MDLabel(text="Input F. Size")
        btn1_ = MDIconButton(icon="minus",
                             size_hint=(1, 1),
                             on_release=lambda x: self.set_text(
                                 self.input_font_size,
                                 str(int(self.input_font_size.text) - 1)
                             ))

        btn2_ = MDIconButton(icon="plus", size_hint=(1, 1),
                             on_release=lambda x: self.set_text(self.input_font_size,
                                                                str(int(self.input_font_size.text) + 1)))

        content.add_widget(lb2)
        content.add_widget(btn1_)
        content.add_widget(self.input_font_size)
        content.add_widget(btn2_)
        content.add_widget(MDSeparator())
        content.add_widget(MDSeparator())
        content.add_widget(MDSeparator())
        content.add_widget(MDSeparator())

        self.mini_result_font_size = MDTextFieldRect(text=config['Fonts']['mini_result_font_size'], halign="center")
        self.mini_result_font_size.bind(text=self.on_config_change)

        lb3 = MDLabel(text="Result F. Size")
        _btn1_ = MDIconButton(icon="minus", size_hint=(1, 1),
                              on_release=lambda x: self.set_text(self.mini_result_font_size,
                                                                 str(int(self.mini_result_font_size.text) - 1)))

        _btn2_ = MDIconButton(icon="plus", size_hint=(1, 1),
                              on_press=lambda x: self.set_text(self.mini_result_font_size,
                                                               str(int(self.mini_result_font_size.text) + 1)))

        content.add_widget(lb3)
        content.add_widget(_btn1_)
        content.add_widget(self.mini_result_font_size)
        content.add_widget(_btn2_)

        self.font_dialog = MDDialog(title="Fonts Options",
                                    size_hint=(0.98, 1),
                                    type="custom",
                                    content_cls=content,
                                    buttons=[
                                        MDRaisedButton(text='Close',
                                                       on_release=lambda x: Item().on_release(2),
                                                       text_color=self.toolbar_for_simple.specific_text_color),
                                        MDRectangleButton(text='Primary Color',
                                                          on_release=lambda x: self.set_color_(0)),

                                        MDRectangleButton(text='Accent Color',
                                                          on_release=lambda x: self.set_color_(0))]
                                    )

        self.accent_dialog = MDDialog(title="Accent Color",
                                      size_hint=(0.98, 1),
                                      type="simple",
                                      items=[
                                          Item(text='Red'),
                                          Item(text='Pink'),
                                          Item(text='Purple'),
                                          Item(text='DeepPurple'),
                                          Item(text='Indigo'),
                                          Item(text='Blue'),
                                          Item(text='LightBlue'),
                                          Item(text='Cyan'),
                                          Item(text='Teal'),
                                          Item(text='Green'),
                                          Item(text='LightGreen'),
                                          Item(text='Lime'),
                                          Item(text='Yellow'),
                                          Item(text='Amber'),
                                          Item(text='Orange'),
                                          Item(text='DeepOrange'),
                                          Item(text='Brown'),
                                          Item(text='Gray'),
                                          Item(text='BlueGray'),
                                      ],
                                      buttons=[
                                          MDRaisedButton(text='Close',
                                                         on_release=lambda x: Item().on_release(0),
                                                         text_color=self.toolbar_for_simple.specific_text_color),
                                          MDRectangleButton(text='Font Settings',
                                                            on_release=lambda x: self.set_color_(2)),
                                          MDRectangleButton(text='Primary Color',
                                                            on_release=lambda x: self.set_color_(0))
                                      ]
                                      )

        self.dialog = MDDialog(title="Primary Color",
                               size_hint=(0.98, 1),
                               type="simple",
                               items=[
                                   Item(text='Red'),
                                   Item(text='Pink'),
                                   Item(text='Purple'),
                                   Item(text='DeepPurple'),
                                   Item(text='Indigo'),
                                   Item(text='Blue'),
                                   Item(text='LightBlue'),
                                   Item(text='Cyan'),
                                   Item(text='Teal'),
                                   Item(text='Green'),
                                   Item(text='LightGreen'),
                                   Item(text='Lime'),
                                   Item(text='Yellow'),
                                   Item(text='Amber'),
                                   Item(text='Orange'),
                                   Item(text='DeepOrange'),
                                   Item(text='Brown'),
                                   Item(text='Gray'),
                                   Item(text='BlueGray'),
                               ],
                               buttons=[
                                   MDRaisedButton(text='Close',
                                                  on_release=lambda x: Item().on_release(1),
                                                  text_color=self.toolbar_for_simple.specific_text_color),
                                   MDRectangleButton(text='Font Settings',
                                                     on_release=lambda x: self.set_color_(2)),
                                   MDRectangleButton(text='Accent Color', on_release=lambda x: self.set_color_(1))
                               ],

                               on_open=self.__init_fonts__

                               )

        self.set_color_(-1)
        config.write()

    def set_color_(self, item):
        if item == 0:
            config['Behavior']['last_dialog'] = "dialog"
            self.font_dialog.dismiss()
            self.accent_dialog.dismiss()
            self.dialog.open()
        elif item == 1:
            config['Behavior']['last_dialog'] = "accent_dialog"
            self.dialog.dismiss()
            self.font_dialog.dismiss()
            self.accent_dialog.open()
        elif item == 2:
            config['Behavior']['last_dialog'] = "font_dialog"
            self.dialog.dismiss()
            self.accent_dialog.dismiss()
            self.font_dialog.open()

        elif item == -1:
            if config['Behavior']['last_dialog'] == "dialog":
                self.set_color_(0)
            if config['Behavior']['last_dialog'] == "accent_dialog":
                self.set_color_(1)
            if config['Behavior']['last_dialog'] == "font_dialog":
                self.set_color_(2)

        elif item in self.dialog.items:
            config['Appearance']['primary_color'] = item.text
            self.theme_cls.primary_palette = item.text
        elif item in self.accent_dialog.items:
            config['Appearance']['accent_color'] = item.text
            self.theme_cls.accent_palette = item.text

        config.write()

        self.__init_fonts__()
        app.numpad.__init_colors__()
        app.minpad.__init_colors__()

    def refresh_drawer(self):
        for item in self.drawer_items:
            if item.text.lower() == self.screenmgr.current:
                item.theme_text_color = "Custom"
                item.bg_color = self.theme_cls.primary_color
                item.text_color = self.toolbar_for_simple.specific_text_color
            else:
                item.theme_text_color = "Primary"
                item.bg_color = []

    def set_screen(self, item):
        self.old_screen = self.screenmgr.current

        if type(item) is str:
            self.screen = item.lower()
        else:
            self.screen = item.text.lower()

        self.screenmgr.current = self.screen
        self.nav_drawer.set_state("close")

        self.refresh_drawer()

    def build(self):
        self.screenmgr = ScreenManager()
        self.screen = MDScreen()

        self.theme_cls.accent_palette = config['Appearance']['accent_color']

        self.nav_drawer = MDNavigationDrawer()
        self.toolbar_for_simple = MDToolbar(title='Leo Calc')
        self.toolbar_for_simple.left_action_items = [['menu', lambda x: self.nav_drawer.set_state("open")]]

        self.toolbar_for_simple.right_action_items = [['settings', lambda x: self.set_color()],
                                                      ['copyright', lambda x: self.set_screen("about")],
                                                      ['close', lambda x: Window.close()]
                                                      ]

        self.toolbar_for_scientific = MDToolbar(title='Leo Calc')
        self.toolbar_for_scientific.left_action_items = [['menu', lambda x: self.nav_drawer.set_state("open")]]

        self.toolbar_for_scientific.right_action_items = [['settings', lambda x: self.set_color()],
                                                          ['copyright', lambda x: self.set_screen("about")],
                                                          ['close', lambda x: Window.close()]
                                                          ]

        self.toolbar_for_about = MDToolbar(title='Leo Calc')
        self.toolbar_for_about.left_action_items = [['menu', lambda x: self.nav_drawer.set_state("open")]]

        self.toolbar_for_about.right_action_items = [['settings', lambda x: self.set_color()],
                                                     ['calculator', lambda x: self.set_screen(self.old_screen)],
                                                     ['close', lambda x: Window.close()]
                                                     ]

        self.screen.add_widget(self.screenmgr)
        self.screen.add_widget(self.nav_drawer)

        Window.bind(on_keyboard=self.on_keyboard)

        return self.screen

    def on_start(self):
        try:
            self.theme_cls.primary_palette = config['Appearance']['primary_color']
            self.theme_cls.accent_palette = config['Appearance']['accent_color']
        except ValueError as err:
            print(err)

        self.title = 'Leo Calc - Modern Edition'
        self.icon = os.path.split(os.path.realpath(sys.argv[0]))[0] + f'/logo-{__app__.lower()}.png'

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        simple = Screen(name="simple")

        simple_lay = MDGridLayout(cols=1)
        simple_lay.add_widget(self.toolbar_for_simple)
        simple.add_widget(simple_lay)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        scientific = Screen(name="scientific")

        scientific_lay = MDGridLayout(cols=1)
        scientific_lay.add_widget(self.toolbar_for_scientific)
        scientific.add_widget(scientific_lay)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        about = Screen(name="about")
        about_lay = MDGridLayout(cols=1)
        about_lay.add_widget(self.toolbar_for_about)
        about.add_widget(about_lay)

        about_lay.add_widget(Image(source=self.icon))

        self.lb1 = MDLabel(text="Leo Calculator Version : %s" % __version__,
                           halign="center",
                           font_style="H6",
                           size_hint=(1, 0.25),
                           text_color=app.theme_cls.accent_color)

        self.lb2 = MDLabel(text="Kivy Version : %s" % kivy.__version__,
                           halign="center",
                           font_style="H6",
                           size_hint=(1, 0.25),
                           text_color=app.theme_cls.accent_color)

        self.lb3 = MDLabel(text="Kivy Material Design Version : %s" % kivymd.__version__,
                           halign="center",
                           font_style="H6",
                           size_hint=(1, 0.25))

        self.lb1.color = app.theme_cls.accent_color
        self.lb2.color = app.theme_cls.accent_color
        self.lb3.color = app.theme_cls.accent_color

        about_lay.add_widget(self.lb1)
        about_lay.add_widget(self.lb2)
        about_lay.add_widget(self.lb3)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        self.main_input = MDTextField(multiline=False, halign='center')
        self.main_input.font_size = config['Fonts']['input_font_size']
        self.mini_result = MDLabel(text='', halign='center')
        self.mini_result.font_size = config['Fonts']['mini_result_font_size']
        self.mini_result.size_hint = (1, 0.1)

        self.mini_result.color = self.theme_cls.accent_color

        ##########################################################################################################################################'
        self.numpad = numpad_layout()

        self.main_input.bind(text=self.numpad.refresh)

        self.minpad = minipad_layout()

        ################## Here Add Widgets ##################################
        simple_lay.add_widget(self.main_input)
        simple_lay.add_widget(self.mini_result)
        simple_lay.add_widget(self.minpad)
        simple_lay.add_widget(self.numpad)

        self.screenmgr.add_widget(simple)
        self.screenmgr.add_widget(scientific)
        self.screenmgr.add_widget(about)
        self.__init_drawer()

        self.main_input.focus = True

        if DEVICE_TYPE != "mobile":
            Window.show()

        self.set_screen(config['Behavior']['last_mode'])

        self.__init_fonts__(key="dark", value=int(config['Appearance']['dark']))
        app.numpad.__init_fonts__()

    def on_stop(self):
        config['Behavior']['last_mode'] = self.screenmgr.current.lower()
        config['Behavior']['size'] = str(Window.size)
        config.write()

    def on_config_change(self, conf=None, section=None, key=None, value=None):
        config['Fonts']['font_size'] = str(self.font_size.text)
        config['Fonts']['input_font_size'] = str(self.input_font_size.text)
        config['Fonts']['mini_result_font_size'] = str(self.mini_result_font_size.text)
        config.write()
        self.__init_fonts__(conf=None, section=None, key=key, value=value)

    def on_keyboard(self, key, scancode=None, codepoint=None, modifier=None, keys=None):
        if codepoint == 40:
            self.numpad.adder(app.numpad.button_equal)
        elif "ctrl" in keys and codepoint == 19:
            self.minpad.clear(app.minpad.button_c)
        elif "ctrl" in keys and codepoint == 26:
            self.main_input.do_undo()
        elif "ctrl" in keys and codepoint == 28:
            self.main_input.do_redo()

    def __init_fonts__(self, conf=None, other=None, section=None, key=None, value=None):

        self.refresh_drawer()

        self.mini_result.color = self.theme_cls.accent_color
        self.mini_result.font_size = config['Fonts']['mini_result_font_size']
        self.lb1.color = self.theme_cls.accent_color
        self.lb2.color = self.theme_cls.accent_color
        self.lb3.color = self.theme_cls.accent_color

        self.numpad.__init_fonts__()
        self.minpad.__init_fonts__()
        self.minpad.__init_colors__()
        self.numpad.__init_colors__()

        if int(config['Appearance']['dark']) == 1:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

        try:
            for item in self.dialog.items:
                if item.text == self.theme_cls.primary_palette:
                    item.theme_text_color = "Custom"
                    item.bg_color = app.theme_cls.primary_color
                    item.text_color = self.toolbar_for_simple.specific_text_color
                else:
                    item.theme_text_color = "Primary"
                    item.bg_color = []

            for item in self.accent_dialog.items:
                if item.text == self.theme_cls.accent_palette:
                    item.theme_text_color = "Custom"
                    item.bg_color = app.theme_cls.primary_color
                    item.text_color = self.toolbar_for_simple.specific_text_color
                else:
                    item.theme_text_color = "Primary"
                    item.bg_color = []
        except:
            pass


if __name__ == '__main__':
    app = App()
    app.run()
