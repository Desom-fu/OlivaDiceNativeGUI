# -*- encoding: utf-8 -*-
'''
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/   
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___   
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/   

@File      :   GUI.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2021, OlivOS-Team
@Desc      :   None
'''

import OlivOS
import OlivaDiceNativeGUI
import OlivaDiceCore
import OlivaDiceOdyssey

import base64
import os
import tkinter
from tkinter import ttk
import webbrowser
import traceback
import threading
import json
import importlib

from PIL import Image
from PIL import ImageTk

dictColorContext = {
    'color_001': '#00A0EA',
    'color_002': '#BBE9FF',
    'color_003': '#40C3FF',
    'color_004': '#FFFFFF',
    'color_005': '#000000',
    'color_006': '#80D7FF'
}

def releaseBase64Data(dir_path, file_name, base64_data):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path) 
    with open(dir_path + '/' + file_name, 'wb+') as tmp:
        tmp.write(base64.b64decode(base64_data))

def get_tree_force(tree_obj):
    return tree_obj.item(tree_obj.focus())

class ConfigUI(object):
    def __init__(self, Model_name, logger_proc = None):
        self.Model_name = Model_name
        self.UIObject = {}
        self.UIData = {}
        self.UIConfig = {}
        self.logger_proc = logger_proc
        self.UIData['flag_open'] = False
        self.UIData['click_record'] = {}
        self.UIConfig.update(dictColorContext)

    def start(self):
        self.UIObject['root'] = tkinter.Toplevel()
        self.UIObject['root'].title('OlivaDice 设置面板')
        self.UIObject['root'].geometry('800x600')
        self.UIObject['root'].minsize(800, 600)
        self.UIObject['root'].resizable(
            width = True,
            height = True
        )
        self.UIObject['root'].grid_rowconfigure(0, weight = 0)
        self.UIObject['root'].grid_rowconfigure(1, weight = 15)
        self.UIObject['root'].grid_columnconfigure(0, weight = 15)
        self.UIObject['root'].grid_columnconfigure(1, weight = 15)
        self.UIObject['root'].configure(bg = self.UIConfig['color_001'])

        self.UIData['hash_now'] = 'unity'

        self.init_hash_Combobox()

        self.init_notebook()

        # 主页
        self.init_frame_main()

        # 回复词
        self.init_frame_str()

        # 配置项
        self.init_frame_console()

        # 骰主列表
        self.init_frame_master()

        # 牌堆管理
        self.UIData['deck_remote_loaded_flag'] = False
        self.init_frame_deck()

        self.UIObject['Notebook_root'].add(self.UIObject['frame_main_root'], text="首页")
        self.UIObject['Notebook_root'].add(self.UIObject['frame_deck_root'], text="牌堆管理")
        self.UIObject['Notebook_root'].add(self.UIObject['frame_str_root'], text="回复词")
        self.UIObject['Notebook_root'].add(self.UIObject['frame_console_root'], text="配置项")
        self.UIObject['Notebook_root'].add(self.UIObject['frame_master_root'], text="骰主列表")

        self.init_data_total()

        self.UIObject['root'].iconbitmap('./resource/tmp_favoricon.ico')
        self.UIObject['root'].mainloop()
        #OlivaDiceNativeGUI.load.flag_open = False

    def init_hash_Combobox(self):
        self.UIData['hash_Combobox_root_StringVar'] = tkinter.StringVar()
        self.UIObject['hash_Combobox_root'] = ttk.Combobox(
            self.UIObject['root'],
            textvariable = self.UIData['hash_Combobox_root_StringVar']
        )
        self.UIObject['hash_Combobox_root'].grid(
            row = 0,
            column = 0,
            sticky = "nsw",
            rowspan = 1,
            columnspan = 1,
            padx = (15, 0),
            pady = (15, 0),
            ipadx = 0,
            ipady = 0
        )
        self.UIObject['hash_Combobox_root'].configure(state='readonly')
        #self.UIObject['hash_Combobox_root'].bind('<<ComboboxSelected>>', lambda x : self.tree_edit_UI_Combobox_ComboboxSelected(x, action, obj_name))
        self.UIData['hash_default'] = 'unity'
        self.UIData['hash_default_key'] = '全局 (不推荐)'
        self.UIData['hash_find'] = {
            self.UIData['hash_default_key']: self.UIData['hash_default']
        }
        self.UIData['hash_list'] = [self.UIData['hash_default_key']]
        for hash_this in OlivaDiceNativeGUI.load.dictBotInfo:
            key_info = '%s | %s' % (
                OlivaDiceNativeGUI.load.dictBotInfo[hash_this].platform['platform'],
                OlivaDiceNativeGUI.load.dictBotInfo[hash_this].id
            )
            self.UIData['hash_list'].append(key_info)
            self.UIData['hash_find'][key_info] = hash_this
            if self.UIData['hash_default'] == 'unity':
                self.UIData['hash_default_key'] = key_info
                self.UIData['hash_default'] = hash_this
        self.UIData['hash_now'] = self.UIData['hash_default']
        self.UIObject['hash_Combobox_root']['value'] = tuple(self.UIData['hash_list'])
        self.UIObject['hash_Combobox_root'].current(
            self.UIData['hash_list'].index(
                self.UIData['hash_default_key']
            )
        )
        self.UIObject['hash_Combobox_root'].bind('<<ComboboxSelected>>', lambda x : self.Combobox_ComboboxSelected(x, 'set', 'hash_Combobox_root'))

        self.UIData['onlineStatus_Label_root_StringVar'] = tkinter.StringVar()
        self.UIObject['onlineStatus_Label_root'] = tkinter.Label(
            self.UIObject['root'],
            textvariable = self.UIData['onlineStatus_Label_root_StringVar']
        )
        self.UIObject['onlineStatus_Label_root'].configure(
            bg = self.UIConfig['color_001'],
            fg = self.UIConfig['color_004']
        )
        self.UIObject['onlineStatus_Label_root'].grid(
            row = 0,
            column = 1,
            sticky = "nse",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 15),
            pady = (15, 0),
            ipadx = 0,
            ipady = 0
        )

    def Combobox_ComboboxSelected(self, action, event, target):
        if target == 'hash_Combobox_root':
            self.UIData['hash_now'] = self.UIData['hash_find'][self.UIData['hash_Combobox_root_StringVar'].get()]
            self.init_data_total()

    def init_notebook(self):
        self.UIData['style'] = ttk.Style(self.UIObject['root'])
        try:
            self.UIData['style'].element_create('Plain.Notebook.tab', "from", 'default')
        except:
            pass
        self.UIData['style'].layout(
            "TNotebook.Tab",
            [('Plain.Notebook.tab', {'children':
                [('Notebook.padding', {'side': 'top', 'children':
                    [('Notebook.focus', {'side': 'top', 'children':
                        [('Notebook.label', {'side': 'top', 'sticky': ''})],
                    'sticky': 'nswe'})],
                'sticky': 'nswe'})],
            'sticky': 'nswe'})])
        self.UIData['style'].configure(
            "TNotebook",
            background = self.UIConfig['color_001'],
            borderwidth = 0,
            relief = tkinter.FLAT,
            padding = [-1, 1, -3, -3],
            tabmargins = [5, 5, 0, 0]
        )
        self.UIData['style'].configure(
            "TNotebook.Tab",
            background = self.UIConfig['color_006'],
            foreground = self.UIConfig['color_001'],
            padding = 4,
            borderwidth = 0,
            font = ('等线', 12, 'bold')
        )
        self.UIData['style'].map(
            "TNotebook.Tab",
            background = [
                ('selected', self.UIConfig['color_004']),
                ('!selected', self.UIConfig['color_003'])
            ],
            foreground = [
                ('selected', self.UIConfig['color_003']),
                ('!selected', self.UIConfig['color_004'])
            ]
        )

        self.UIObject['Notebook_root'] = ttk.Notebook(self.UIObject['root'], style = 'TNotebook')
        self.UIObject['Notebook_root'].grid(
            row = 1,
            column = 0,
            sticky = "nsew",
            rowspan = 1,
            columnspan = 2,
            padx = (15, 15),
            pady = (8, 15),
            ipadx = 0,
            ipady = 0
        )
        self.UIObject['Notebook_root'].grid_rowconfigure(0, weight = 0)
        self.UIObject['Notebook_root'].grid_rowconfigure(1, weight = 15)
        self.UIObject['Notebook_root'].grid_columnconfigure(0, weight = 15)
        self.UIObject['Notebook_root'].bind('<<NotebookTabChanged>>', lambda x : self.onNotebookTabChanged(x))

    def init_frame_main(self):
        self.UIObject['frame_main_root'] = tkinter.Frame(self.UIObject['Notebook_root'])
        self.UIObject['frame_main_root'].configure(relief = tkinter.FLAT)
        self.UIObject['frame_main_root'].grid(
            row = 1,
            column = 0,
            sticky = "nsew",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )
        self.UIObject['frame_main_root'].grid_rowconfigure(0, weight = 0)
        self.UIObject['frame_main_root'].grid_rowconfigure(1, weight = 0)
        self.UIObject['frame_main_root'].grid_rowconfigure(2, weight = 0)
        self.UIObject['frame_main_root'].grid_rowconfigure(3, weight = 15)
        self.UIObject['frame_main_root'].grid_rowconfigure(4, weight = 0)
        self.UIObject['frame_main_root'].grid_columnconfigure(0, weight = 15)
        self.UIObject['frame_main_root'].grid_columnconfigure(1, weight = 15)
        self.UIObject['frame_main_root'].grid_columnconfigure(2, weight = 15)
        self.UIObject['frame_main_root'].grid_columnconfigure(3, weight = 15)
        self.UIObject['frame_main_root'].grid_columnconfigure(4, weight = 15)
        self.UIObject['frame_main_root'].grid_columnconfigure(5, weight = 15)
        self.UIObject['frame_main_root'].grid_columnconfigure(6, weight = 15)
        self.UIObject['frame_main_root'].grid_columnconfigure(7, weight = 15)
        self.UIObject['frame_main_root'].grid_columnconfigure(8, weight = 15)
        self.UIObject['frame_main_root'].configure(bg = self.UIConfig['color_001'], borderwidth = 0)

        self.UIObject['label_master_token'] = tkinter.Label(
            self.UIObject['frame_main_root'],
            text = '点击以下按钮复制指令，并在聊天窗口中发送给骰子，即可成为骰主！'
        )
        self.UIObject['label_master_token'].configure(
            bg = self.UIConfig['color_001'],
            fg = self.UIConfig['color_004'],
            font = ('等线', 18, 'bold')
        )
        self.UIObject['label_master_token'].grid(
            row = 0,
            column = 0,
            sticky = "nwe",
            rowspan = 1,
            columnspan = 9,
            padx = (0, 0),
            pady = (15, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIData['buttom_master_token_copy_StringVar'] = tkinter.StringVar()
        self.process_msg()
        self.UIObject['buttom_master_token_copy'] = tkinter.Button(
            self.UIObject['frame_main_root'],
            textvariable = self.UIData['buttom_master_token_copy_StringVar'],
            command = lambda : self.master_token_copy_action(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            font = ('等线', 16, 'bold')
        )
        self.UIObject['buttom_master_token_copy'].bind('<Enter>', lambda x : self.buttom_action('buttom_master_token_copy', '<Enter>'))
        self.UIObject['buttom_master_token_copy'].bind('<Leave>', lambda x : self.buttom_action('buttom_master_token_copy', '<Leave>'))
        self.UIObject['buttom_master_token_copy'].grid(
            row = 1,
            column = 0,
            sticky = "nwe",
            rowspan = 1,
            columnspan = 9,
            padx = (60, 60),
            pady = (15, 8),
            ipadx = 0,
            ipady = 0
        )

        releaseBase64Data('./resource', 'tmp_icon.png', OlivaDiceNativeGUI.imageData.icon)
        self.UIObject['icon_img_data'] = Image.open('./resource/tmp_icon.png')
        try:
            self.UIObject['icon_img_data'] = self.UIObject['icon_img_data'].resize((192 * 2, 108 * 2), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)
        except AttributeError:
            self.UIObject['icon_img_data'] = self.UIObject['icon_img_data'].resize((192 * 2, 108 * 2), Image.ANTIALIAS)
        self.UIObject['icon_img'] = ImageTk.PhotoImage(self.UIObject['icon_img_data'])
        self.UIObject['icon_label'] = tkinter.Label(self.UIObject['frame_main_root'])
        self.UIObject['icon_label'].config(image = self.UIObject['icon_img'])
        self.UIObject['icon_label'].image = self.UIObject['icon_img']
        self.UIObject['icon_label'].configure(
            bg = self.UIConfig['color_001']
        )
        self.UIObject['icon_label'].grid(
            row = 2,
            column = 0,
            sticky = "nwe",
            rowspan = 1,
            columnspan = 9,
            padx = (15, 15),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['label_bot_info'] = tkinter.Label(
            self.UIObject['frame_main_root'],
            text = '\n'.join(
                [
                    OlivaDiceCore.data.bot_info,
                    '',
                    '世界是属于每一个人的。要创造一个充满逻辑并尊重每一个人的世界。',
                    '                                        ——《Новый Элемент Расселения》A.D.1960 Москва'
                ]
            )
        )
        self.UIObject['label_bot_info'].configure(
            bg = self.UIConfig['color_001'],
            fg = self.UIConfig['color_004'],
            font = ('等线', 14, 'bold')
        )
        self.UIObject['label_bot_info'].grid(
            row = 3,
            column = 0,
            sticky = "nwe",
            rowspan = 1,
            columnspan = 9,
            padx = (0, 0),
            pady = (15, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_share_1'] = tkinter.Button(
            self.UIObject['frame_main_root'],
            text = '论坛地址',
            command = lambda : self.show_project_site('https://forum.olivos.run/'),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_share_1'].bind('<Enter>', lambda x : self.buttom_action('buttom_share_1', '<Enter>'))
        self.UIObject['buttom_share_1'].bind('<Leave>', lambda x : self.buttom_action('buttom_share_1', '<Leave>'))
        self.UIObject['buttom_share_1'].grid(
            row = 4,
            column = 0,
            sticky = "nwe",
            rowspan = 1,
            columnspan = 2,
            padx = (15, 0),
            pady = (15, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_share_2'] = tkinter.Button(
            self.UIObject['frame_main_root'],
            text = '使用手册',
            command = lambda : self.show_project_site('https://wiki.dice.center/'),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_share_2'].bind('<Enter>', lambda x : self.buttom_action('buttom_share_2', '<Enter>'))
        self.UIObject['buttom_share_2'].bind('<Leave>', lambda x : self.buttom_action('buttom_share_2', '<Leave>'))
        self.UIObject['buttom_share_2'].grid(
            row = 4,
            column = 2,
            sticky = "nwe",
            rowspan = 1,
            columnspan = 2,
            padx = (15, 0),
            pady = (15, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_share_3'] = tkinter.Button(
            self.UIObject['frame_main_root'],
            text = '项目源码',
            command = lambda : self.show_project_site('https://github.com/OlivOS-Team/OlivaDiceCore'),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_share_3'].bind('<Enter>', lambda x : self.buttom_action('buttom_share_3', '<Enter>'))
        self.UIObject['buttom_share_3'].bind('<Leave>', lambda x : self.buttom_action('buttom_share_3', '<Leave>'))
        self.UIObject['buttom_share_3'].grid(
            row = 4,
            column = 5,
            sticky = "nwe",
            rowspan = 1,
            columnspan = 2,
            padx = (15, 0),
            pady = (15, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_share_4'] = tkinter.Button(
            self.UIObject['frame_main_root'],
            text = '赞助项目',
            command = lambda : self.show_project_site('https://afdian.net/@OlivOS'),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_share_4'].bind('<Enter>', lambda x : self.buttom_action('buttom_share_4', '<Enter>'))
        self.UIObject['buttom_share_4'].bind('<Leave>', lambda x : self.buttom_action('buttom_share_4', '<Leave>'))
        self.UIObject['buttom_share_4'].grid(
            row = 4,
            column = 7,
            sticky = "nwe",
            rowspan = 1,
            columnspan = 2,
            padx = (15, 0),
            pady = (15, 0),
            ipadx = 0,
            ipady = 0
        )

    def master_token_copy_action(self):
        self.UIObject['root'].clipboard_clear()
        self.UIObject['root'].clipboard_append(self.UIData['buttom_master_token_copy_StringVar'].get())
        self.UIObject['root'].update()
        tkinter.messagebox.showinfo('已完成复制', '在聊天窗口中发送给骰子，即可成为骰主！')

    def process_msg(self):
        self.UIObject['root'].after(1000,self.process_msg)
        self.UIData['buttom_master_token_copy_StringVar'].set('.master %s' % OlivaDiceCore.data.bot_content['masterKey'])

    def show_project_site(self, url):
        tkinter.messagebox.showinfo("提示", "将通过浏览器访问 " + url)
        try:
            webbrowser.open(url)
        except webbrowser.Error as error_info:
            tkinter.messagebox.showerror("webbrowser.Error", error_info)

    def buttom_action(self, name, action):
        if name in self.UIObject:
            if action == '<Enter>':
                self.UIObject[name].configure(bg = self.UIConfig['color_006'])
            if action == '<Leave>':
                self.UIObject[name].configure(bg = self.UIConfig['color_003'])

    def init_frame_str(self):
        self.UIObject['frame_str_root'] = tkinter.Frame(self.UIObject['Notebook_root'])
        self.UIObject['frame_str_root'].configure(relief = tkinter.FLAT)
        self.UIObject['frame_str_root'].grid(
            row = 1,
            column = 0,
            sticky = "nsew",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )
        self.UIObject['frame_str_root'].grid_rowconfigure(0, weight = 0)
        self.UIObject['frame_str_root'].grid_rowconfigure(1, weight = 15)
        self.UIObject['frame_str_root'].grid_columnconfigure(0, weight = 15)
        self.UIObject['frame_str_root'].grid_columnconfigure(1, weight = 0)
        self.UIObject['frame_str_root'].configure(bg = self.UIConfig['color_001'], borderwidth = 0)

        self.UIObject['tree_str'] = ttk.Treeview(self.UIObject['frame_str_root'])
        self.UIObject['tree_str']['show'] = 'headings'
        self.UIObject['tree_str']['columns'] = ('KEY', 'NOTE', 'DATA')
        self.UIObject['tree_str'].column('KEY', width = 140)
        self.UIObject['tree_str'].column('NOTE', width = 275)
        self.UIObject['tree_str'].column('DATA', width = 275)
        self.UIObject['tree_str'].heading('KEY', text = '条目')
        self.UIObject['tree_str'].heading('NOTE', text = '说明')
        self.UIObject['tree_str'].heading('DATA', text = '内容')
        self.UIObject['tree_str'].grid(
            row = 1,
            column = 0,
            sticky = "nsew",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )
        self.UIObject['tree_rightkey_menu'] = tkinter.Menu(self.UIObject['root'], tearoff = False)
        self.UIObject['tree_str'].bind('<Button-3>', lambda x : self.tree_str_rightKey(x))
        self.UIObject['tree_str_yscroll'] = ttk.Scrollbar(
            self.UIObject['frame_str_root'],
            orient = "vertical",
            command = self.UIObject['tree_str'].yview
        )
        self.UIObject['tree_str'].configure(
            yscrollcommand = self.UIObject['tree_str_yscroll'].set
        )
        self.UIObject['tree_str_yscroll'].grid(
            row = 1,
            column = 1,
            sticky = "nsw",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['button_frame_str'] = tkinter.Frame(self.UIObject['frame_str_root'])
        self.UIObject['button_frame_str'].configure(bg = self.UIConfig['color_001'])
        self.UIObject['button_frame_str'].grid(
            row = 2,
            column = 0,
            sticky = "nsew",
            rowspan = 1,
            columnspan = 2,
            padx = (15, 15),
            pady = (8, 0)
        )

        self.UIObject['buttom_reset_str'] = tkinter.Button(
            self.UIObject['button_frame_str'],
            text = '恢复默认回复',
            command = lambda : self.reset_str_confirm(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_reset_str'].bind('<Enter>', lambda x : self.buttom_action('buttom_reset_str', '<Enter>'))
        self.UIObject['buttom_reset_str'].bind('<Leave>', lambda x : self.buttom_action('buttom_reset_str', '<Leave>'))
        self.UIObject['buttom_reset_str'].pack(side = tkinter.LEFT, padx = (0, 5))

        self.UIObject['buttom_import_str'] = tkinter.Button(
            self.UIObject['button_frame_str'],
            text = '导入回复',
            command = lambda : self.import_str_config(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_import_str'].bind('<Enter>', lambda x : self.buttom_action('buttom_import_str', '<Enter>'))
        self.UIObject['buttom_import_str'].bind('<Leave>', lambda x : self.buttom_action('buttom_import_str', '<Leave>'))
        self.UIObject['buttom_import_str'].pack(side = tkinter.LEFT, padx = (0, 5))

        self.UIObject['buttom_export_str'] = tkinter.Button(
            self.UIObject['button_frame_str'],
            text = '导出回复',
            command = lambda : self.export_str_config(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_export_str'].bind('<Enter>', lambda x : self.buttom_action('buttom_export_str', '<Enter>'))
        self.UIObject['buttom_export_str'].bind('<Leave>', lambda x : self.buttom_action('buttom_export_str', '<Leave>'))
        self.UIObject['buttom_export_str'].pack(side = tkinter.LEFT, padx = (0, 5))

        self.UIObject['buttom_refresh_str'] = tkinter.Button(
            self.UIObject['button_frame_str'],
            text = '刷新回复',
            command = lambda : self.refresh_str_config(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_refresh_str'].bind('<Enter>', lambda x : self.buttom_action('buttom_refresh_str', '<Enter>'))
        self.UIObject['buttom_refresh_str'].bind('<Leave>', lambda x : self.buttom_action('buttom_refresh_str', '<Leave>'))
        self.UIObject['buttom_refresh_str'].pack(side = tkinter.LEFT, padx = (0, 5))

        self.UIObject['buttom_edit_str'] = tkinter.Button(
            self.UIObject['button_frame_str'],
            text = '编辑',
            command = lambda : self.tree_str_edit(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_edit_str'].bind('<Enter>', lambda x : self.buttom_action('buttom_edit_str', '<Enter>'))
        self.UIObject['buttom_edit_str'].bind('<Leave>', lambda x : self.buttom_action('buttom_edit_str', '<Leave>'))
        self.UIObject['buttom_edit_str'].pack(side = tkinter.RIGHT)
        
        self.UIObject['buttom_reset_delete_str'] = tkinter.Button(
            self.UIObject['button_frame_str'],
            text = '恢复/删除',
            command = lambda : self.reset_selected_str(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_reset_delete_str'].bind('<Enter>', lambda x : self.buttom_action('buttom_reset_delete_str', '<Enter>'))
        self.UIObject['buttom_reset_delete_str'].bind('<Leave>', lambda x : self.buttom_action('buttom_reset_delete_str', '<Leave>'))
        self.UIObject['buttom_reset_delete_str'].pack(side = tkinter.RIGHT, padx = (0, 5))

    def init_frame_console(self):
        self.UIObject['frame_console_root'] = tkinter.Frame(self.UIObject['Notebook_root'])
        self.UIObject['frame_console_root'].configure(relief = tkinter.FLAT)
        self.UIObject['frame_console_root'].grid(
            row = 1,
            column = 0,
            sticky = "nsew",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )
        self.UIObject['frame_console_root'].grid_rowconfigure(0, weight = 0)
        self.UIObject['frame_console_root'].grid_rowconfigure(1, weight = 15)
        self.UIObject['frame_console_root'].grid_rowconfigure(2, weight = 0)
        self.UIObject['frame_console_root'].grid_columnconfigure(0, weight = 15)
        self.UIObject['frame_console_root'].configure(bg = self.UIConfig['color_001'], borderwidth = 0)

        self.UIObject['tree_console'] = ttk.Treeview(self.UIObject['frame_console_root'])
        self.UIObject['tree_console']['show'] = 'headings'
        self.UIObject['tree_console']['columns'] = ('KEY', 'NOTE', 'DATA')
        self.UIObject['tree_console'].column('KEY', width = 140)
        self.UIObject['tree_console'].column('NOTE', width = 500)
        self.UIObject['tree_console'].column('DATA', width = 50)
        self.UIObject['tree_console'].heading('KEY', text = '条目')
        self.UIObject['tree_console'].heading('NOTE', text = '说明')
        self.UIObject['tree_console'].heading('DATA', text = '内容')
        self.UIObject['tree_console'].grid(
            row = 1,
            column = 0,
            sticky = "nsew",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )
        self.UIObject['tree_rightkey_menu'] = tkinter.Menu(self.UIObject['root'], tearoff = False)
        self.UIObject['tree_console'].bind('<Button-3>', lambda x : self.tree_console_rightKey(x))
        self.UIObject['tree_console_yscroll'] = ttk.Scrollbar(
            self.UIObject['frame_console_root'],
            orient = "vertical",
            command = self.UIObject['tree_console'].yview
        )
        self.UIObject['tree_console'].configure(
            yscrollcommand = self.UIObject['tree_console_yscroll'].set
        )
        self.UIObject['tree_console_yscroll'].grid(
            row = 1,
            column = 1,
            sticky = "nsw",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['button_frame_console'] = tkinter.Frame(self.UIObject['frame_console_root'])
        self.UIObject['button_frame_console'].configure(bg = self.UIConfig['color_001'])
        self.UIObject['button_frame_console'].grid(
            row = 2,
            column = 0,
            sticky = "nsew",
            rowspan = 1,
            columnspan = 2,
            padx = (15, 15),
            pady = (8, 0)
        )

        self.UIObject['buttom_reset_console'] = tkinter.Button(
            self.UIObject['button_frame_console'],
            text = '恢复默认配置',
            command = lambda : self.reset_console_confirm(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_reset_console'].bind('<Enter>', lambda x : self.buttom_action('buttom_reset_console', '<Enter>'))
        self.UIObject['buttom_reset_console'].bind('<Leave>', lambda x : self.buttom_action('buttom_reset_console', '<Leave>'))
        self.UIObject['buttom_reset_console'].pack(side = tkinter.LEFT, padx = (0, 5))

        self.UIObject['buttom_import_console'] = tkinter.Button(
            self.UIObject['button_frame_console'],
            text = '导入配置',
            command = lambda : self.import_console_config(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_import_console'].bind('<Enter>', lambda x : self.buttom_action('buttom_import_console', '<Enter>'))
        self.UIObject['buttom_import_console'].bind('<Leave>', lambda x : self.buttom_action('buttom_import_console', '<Leave>'))
        self.UIObject['buttom_import_console'].pack(side = tkinter.LEFT, padx = (0, 5))

        self.UIObject['buttom_export_console'] = tkinter.Button(
            self.UIObject['button_frame_console'],
            text = '导出配置',
            command = lambda : self.export_console_config(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_export_console'].bind('<Enter>', lambda x : self.buttom_action('buttom_export_console', '<Enter>'))
        self.UIObject['buttom_export_console'].bind('<Leave>', lambda x : self.buttom_action('buttom_export_console', '<Leave>'))
        self.UIObject['buttom_export_console'].pack(side = tkinter.LEFT, padx = (0, 5))

        self.UIObject['buttom_refresh_console'] = tkinter.Button(
            self.UIObject['button_frame_console'],
            text = '刷新配置',
            command = lambda : self.refresh_console_config(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_refresh_console'].bind('<Enter>', lambda x : self.buttom_action('buttom_refresh_console', '<Enter>'))
        self.UIObject['buttom_refresh_console'].bind('<Leave>', lambda x : self.buttom_action('buttom_refresh_console', '<Leave>'))
        self.UIObject['buttom_refresh_console'].pack(side = tkinter.LEFT, padx = (0, 5))

        self.UIObject['buttom_edit_console'] = tkinter.Button(
            self.UIObject['button_frame_console'],
            text = '编辑',
            command = lambda : self.tree_console_edit(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_edit_console'].bind('<Enter>', lambda x : self.buttom_action('buttom_edit_console', '<Enter>'))
        self.UIObject['buttom_edit_console'].bind('<Leave>', lambda x : self.buttom_action('buttom_edit_console', '<Leave>'))
        self.UIObject['buttom_edit_console'].pack(side = tkinter.RIGHT)

        self.UIObject['buttom_reset_delete_console'] = tkinter.Button(
            self.UIObject['button_frame_console'],
            text = '恢复/删除',
            command = lambda : self.reset_selected_console(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
            width = 12
        )
        self.UIObject['buttom_reset_delete_console'].bind('<Enter>', lambda x : self.buttom_action('buttom_reset_delete_console', '<Enter>'))
        self.UIObject['buttom_reset_delete_console'].bind('<Leave>', lambda x : self.buttom_action('buttom_reset_delete_console', '<Leave>'))
        self.UIObject['buttom_reset_delete_console'].pack(side = tkinter.RIGHT, padx = (0, 5))

    def init_frame_master(self):
        self.UIObject['frame_master_root'] = tkinter.Frame(self.UIObject['Notebook_root'])
        self.UIObject['frame_master_root'].configure(relief = tkinter.FLAT)
        self.UIObject['frame_master_root'].grid(
            row = 1,
            column = 0,
            sticky = "nsew",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )
        self.UIObject['frame_master_root'].grid_rowconfigure(0, weight = 0)
        self.UIObject['frame_master_root'].grid_rowconfigure(1, weight = 0)
        self.UIObject['frame_master_root'].grid_rowconfigure(2, weight = 0)
        self.UIObject['frame_master_root'].grid_rowconfigure(3, weight = 15)
        self.UIObject['frame_master_root'].grid_columnconfigure(0, weight = 5)
        self.UIObject['frame_master_root'].grid_columnconfigure(1, weight = 5)
        self.UIObject['frame_master_root'].grid_columnconfigure(2, weight = 5)
        self.UIObject['frame_master_root'].grid_columnconfigure(3, weight = 5)
        self.UIObject['frame_master_root'].grid_columnconfigure(4, weight = 5)
        self.UIObject['frame_master_root'].grid_columnconfigure(5, weight = 0)
        self.UIObject['frame_master_root'].grid_columnconfigure(6, weight = 15)
        self.UIObject['frame_master_root'].grid_columnconfigure(7, weight = 0)
        self.UIObject['frame_master_root'].configure(bg = self.UIConfig['color_001'], borderwidth = 0)

        self.UIObject['tree_master'] = ttk.Treeview(self.UIObject['frame_master_root'])
        self.UIObject['tree_master']['show'] = 'headings'
        self.UIObject['tree_master']['columns'] = ('KEY', 'NAME')
        self.UIObject['tree_master'].column('KEY', width = 50)
        self.UIObject['tree_master'].column('NAME', width = 50)
        self.UIObject['tree_master'].heading('KEY', text = '账号')
        self.UIObject['tree_master'].heading('NAME', text = '昵称')
        self.UIObject['tree_master'].grid(
            row = 0,
            column = 6,
            sticky = "nsew",
            rowspan = 4,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )
        self.UIObject['tree_rightkey_menu'] = tkinter.Menu(self.UIObject['root'], tearoff = False)
        #self.UIObject['tree_master'].bind('<Button-3>', lambda x : self.tree_master_rightKey(x))
        self.UIObject['tree_master'].bind('<<TreeviewSelect>>', lambda x : self.treeSelect('tree_master', x))
        self.UIObject['tree_master_yscroll'] = ttk.Scrollbar(
            self.UIObject['frame_master_root'],
            orient = "vertical",
            command = self.UIObject['tree_master'].yview
        )
        self.UIObject['tree_master'].configure(
            yscrollcommand = self.UIObject['tree_master_yscroll'].set
        )
        self.UIObject['tree_master_yscroll'].grid(
            row = 0,
            column = 7,
            sticky = "nsw",
            rowspan = 4,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIData['entry_master_StringVar'] = tkinter.StringVar()
        self.UIObject['entry_master'] = tkinter.Entry(
            self.UIObject['frame_master_root'],
            textvariable = self.UIData['entry_master_StringVar']
        )
        self.UIObject['entry_master'].configure(
            bg = self.UIConfig['color_006'],
            fg = self.UIConfig['color_001'],
            font = ('等线', 12, 'bold'),
            bd = 0,
            justify = 'center'
        )
        self.UIObject['entry_master'].grid(
            row = 0,
            column = 1,
            sticky = "nwe",
            rowspan = 1,
            columnspan = 3,
            padx = (0, 0),
            pady = (180, 0),
            ipadx = 4,
            ipady = 8
        )

        self.UIObject['buttom_master_add'] = tkinter.Button(
            self.UIObject['frame_master_root'],
            text = '添加',
            command = lambda : self.tree_master_config('add'),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
        )
        self.UIObject['buttom_master_add'].bind('<Enter>', lambda x : self.buttom_action('buttom_master_add', '<Enter>'))
        self.UIObject['buttom_master_add'].bind('<Leave>', lambda x : self.buttom_action('buttom_master_add', '<Leave>'))
        self.UIObject['buttom_master_add'].grid(
            row = 1,
            column = 1,
            sticky = "new",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 0),
            pady = (45, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_master_del'] = tkinter.Button(
            self.UIObject['frame_master_root'],
            text = '删除',
            command = lambda : self.tree_master_config('del'),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
        )
        self.UIObject['buttom_master_del'].bind('<Enter>', lambda x : self.buttom_action('buttom_master_del', '<Enter>'))
        self.UIObject['buttom_master_del'].bind('<Leave>', lambda x : self.buttom_action('buttom_master_del', '<Leave>'))
        self.UIObject['buttom_master_del'].grid(
            row = 1,
            column = 3,
            sticky = "new",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 0),
            pady = (45, 0),
            ipadx = 0,
            ipady = 0
        )

    def init_frame_deck(self):
        self.UIObject['frame_deck_root'] = tkinter.Frame(self.UIObject['Notebook_root'])
        self.UIObject['frame_deck_root'].configure(relief = tkinter.FLAT)
        self.UIObject['frame_deck_root'].grid(
            row = 1,
            column = 0,
            sticky = "nsew",
            rowspan = 1,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )
        self.UIObject['frame_deck_root'].grid_rowconfigure(0, weight = 0)
        self.UIObject['frame_deck_root'].grid_rowconfigure(1, weight = 0)
        self.UIObject['frame_deck_root'].grid_rowconfigure(2, weight = 0)
        self.UIObject['frame_deck_root'].grid_rowconfigure(3, weight = 0)
        self.UIObject['frame_deck_root'].grid_rowconfigure(4, weight = 0)
        self.UIObject['frame_deck_root'].grid_rowconfigure(5, weight = 0)
        self.UIObject['frame_deck_root'].grid_rowconfigure(6, weight = 0)
        self.UIObject['frame_deck_root'].grid_rowconfigure(7, weight = 15)
        self.UIObject['frame_deck_root'].grid_columnconfigure(0, weight = 30)
        self.UIObject['frame_deck_root'].grid_columnconfigure(1, weight = 0)
        self.UIObject['frame_deck_root'].grid_columnconfigure(2, weight = 0)
        self.UIObject['frame_deck_root'].grid_columnconfigure(3, weight = 0)
        self.UIObject['frame_deck_root'].grid_columnconfigure(4, weight = 0)
        self.UIObject['frame_deck_root'].grid_columnconfigure(5, weight = 30)
        self.UIObject['frame_deck_root'].grid_columnconfigure(6, weight = 0)
        tmp_tree_rowspan = 7
        self.UIObject['frame_deck_root'].configure(bg = self.UIConfig['color_001'], borderwidth = 0)
        self.UIData['deck_local_now'] = None
        self.UIData['deck_remote_now'] = None
        self.UIData['label_deck_remote_note_StringVar_origin'] = '牌堆市场 ☁'
        self.UIData['label_deck_remote_note_StringVar_load'] = '正在刷新 ☁'
        self.UIData['label_deck_remote_note_StringVar_failed'] = '刷新失败 ☁'
        self.UIData['label_deck_remote_note_StringVar'] = tkinter.StringVar()

        self.UIObject['label_deck_local_note'] = tkinter.Label(
            self.UIObject['frame_deck_root'],
            text = '本地牌堆'
        )
        self.UIObject['label_deck_local_note'].configure(
            bg = self.UIConfig['color_001'],
            fg = self.UIConfig['color_004'],
            font = ('等线', 12)
        )
        self.UIObject['label_deck_local_note'].grid(
            row = 0,
            column = 0,
            sticky = "nw",
            rowspan = 1,
            columnspan = 9,
            padx = (0, 0),
            pady = (10, 5),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['tree_deck_local'] = ttk.Treeview(self.UIObject['frame_deck_root'])
        self.UIObject['tree_deck_local']['show'] = 'headings'
        self.UIObject['tree_deck_local']['columns'] = ('KEY')
        self.UIObject['tree_deck_local'].column('KEY', width = 50)
        self.UIObject['tree_deck_local'].heading('KEY', text = '牌堆名')
        self.UIObject['tree_deck_local'].grid(
            row = 1,
            column = 0,
            sticky = "nsew",
            rowspan = tmp_tree_rowspan,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )
        #self.UIObject['tree_rightkey_menu'] = tkinter.Menu(self.UIObject['root'], tearoff = False)
        #self.UIObject['tree_master'].bind('<Button-3>', lambda x : self.tree_master_rightKey(x))
        self.UIObject['tree_deck_local'].bind('<<TreeviewSelect>>', lambda x : self.treeSelect('tree_deck_local', x))
        self.UIObject['tree_deck_local_yscroll'] = ttk.Scrollbar(
            self.UIObject['frame_deck_root'],
            orient = "vertical",
            command = self.UIObject['tree_deck_local'].yview
        )
        self.UIObject['tree_deck_local'].configure(
            yscrollcommand = self.UIObject['tree_deck_local_yscroll'].set
        )
        self.UIObject['tree_deck_local_yscroll'].grid(
            row = 1,
            column = 1,
            sticky = "nsw",
            rowspan = tmp_tree_rowspan,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_deck_reload'] = tkinter.Button(
            self.UIObject['frame_deck_root'],
            text = '重载牌堆',
            command = self.reloadDeck_local_gen(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
        )
        self.UIObject['buttom_deck_reload'].configure(
            font = ('等线', 12)
        )
        self.UIObject['buttom_deck_reload'].bind('<Enter>', lambda x : self.buttom_action('buttom_deck_reload', '<Enter>'))
        self.UIObject['buttom_deck_reload'].bind('<Leave>', lambda x : self.buttom_action('buttom_deck_reload', '<Leave>'))
        self.UIObject['buttom_deck_reload'].grid(
            row = 1,
            column = 2,
            sticky = "new",
            rowspan = 1,
            columnspan = 3,
            padx = (15, 15),
            pady = (0, 2),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_deck_remove'] = tkinter.Button(
            self.UIObject['frame_deck_root'],
            text = '删除牌堆 ×',
            command = self.removeDeck_gen(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
        )
        self.UIObject['buttom_deck_remove'].configure(
            font = ('等线', 12)
        )
        self.UIObject['buttom_deck_remove'].bind('<Enter>', lambda x : self.buttom_action('buttom_deck_remove', '<Enter>'))
        self.UIObject['buttom_deck_remove'].bind('<Leave>', lambda x : self.buttom_action('buttom_deck_remove', '<Leave>'))
        self.UIObject['buttom_deck_remove'].grid(
            row = 2,
            column = 2,
            sticky = "new",
            rowspan = 1,
            columnspan = 1,
            padx = (15, 2),
            pady = (2, 2),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_deck_dir_unity'] = tkinter.Button(
            self.UIObject['frame_deck_root'],
            text = '打开全局目录',
            command = self.openDeckPath_gen(flagUnity = True),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
        )
        self.UIObject['buttom_deck_dir_unity'].configure(
            font = ('等线', 12)
        )
        self.UIObject['buttom_deck_dir_unity'].bind('<Enter>', lambda x : self.buttom_action('buttom_deck_dir_unity', '<Enter>'))
        self.UIObject['buttom_deck_dir_unity'].bind('<Leave>', lambda x : self.buttom_action('buttom_deck_dir_unity', '<Leave>'))
        self.UIObject['buttom_deck_dir_unity'].grid(
            row = 5,
            column = 2,
            sticky = "new",
            rowspan = 1,
            columnspan = 1,
            padx = (15, 2),
            pady = (60, 2),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_deck_dir_this'] = tkinter.Button(
            self.UIObject['frame_deck_root'],
            text = '打开本机目录',
            command = self.openDeckPath_gen(flagUnity = False),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
        )
        self.UIObject['buttom_deck_dir_this'].configure(
            font = ('等线', 12)
        )
        self.UIObject['buttom_deck_dir_this'].bind('<Enter>', lambda x : self.buttom_action('buttom_deck_dir_this', '<Enter>'))
        self.UIObject['buttom_deck_dir_this'].bind('<Leave>', lambda x : self.buttom_action('buttom_deck_dir_this', '<Leave>'))
        self.UIObject['buttom_deck_dir_this'].grid(
            row = 6,
            column = 2,
            sticky = "new",
            rowspan = 1,
            columnspan = 1,
            padx = (15, 2),
            pady = (2, 2),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_deck_install_unity'] = tkinter.Button(
            self.UIObject['frame_deck_root'],
            text = '安装至全局 <<',
            command = self.installDeck_gen(flagUnity = True),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
        )
        self.UIObject['buttom_deck_install_unity'].configure(
            font = ('等线', 12)
        )
        self.UIObject['buttom_deck_install_unity'].bind('<Enter>', lambda x : self.buttom_action('buttom_deck_install_unity', '<Enter>'))
        self.UIObject['buttom_deck_install_unity'].bind('<Leave>', lambda x : self.buttom_action('buttom_deck_install_unity', '<Leave>'))
        self.UIObject['buttom_deck_install_unity'].grid(
            row = 2,
            column = 4,
            sticky = "new",
            rowspan = 1,
            columnspan = 1,
            padx = (2, 15),
            pady = (2, 2),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_deck_install_this'] = tkinter.Button(
            self.UIObject['frame_deck_root'],
            text = '安装至本机 <<',
            command = self.installDeck_gen(flagUnity = False),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
        )
        self.UIObject['buttom_deck_install_this'].configure(
            font = ('等线', 12)
        )
        self.UIObject['buttom_deck_install_this'].bind('<Enter>', lambda x : self.buttom_action('buttom_deck_install_this', '<Enter>'))
        self.UIObject['buttom_deck_install_this'].bind('<Leave>', lambda x : self.buttom_action('buttom_deck_install_this', '<Leave>'))
        self.UIObject['buttom_deck_install_this'].grid(
            row = 3,
            column = 4,
            sticky = "new",
            rowspan = 1,
            columnspan = 1,
            padx = (2, 15),
            pady = (2, 2),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['buttom_deck_upload'] = tkinter.Button(
            self.UIObject['frame_deck_root'],
            text = '上传牌堆',
            command = self.uploadDeckUrl_gen(),
            bd = 0,
            activebackground = self.UIConfig['color_002'],
            activeforeground = self.UIConfig['color_001'],
            bg = self.UIConfig['color_003'],
            fg = self.UIConfig['color_004'],
            relief = 'groove',
            height = 2,
        )
        self.UIObject['buttom_deck_upload'].configure(
            font = ('等线', 12)
        )
        self.UIObject['buttom_deck_upload'].bind('<Enter>', lambda x : self.buttom_action('buttom_deck_upload', '<Enter>'))
        self.UIObject['buttom_deck_upload'].bind('<Leave>', lambda x : self.buttom_action('buttom_deck_upload', '<Leave>'))
        self.UIObject['buttom_deck_upload'].grid(
            row = 6,
            column = 4,
            sticky = "new",
            rowspan = 1,
            columnspan = 1,
            padx = (2, 15),
            pady = (2, 2),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['label_deck_remote_note'] = tkinter.Label(
            self.UIObject['frame_deck_root'],
            textvariable = self.UIData['label_deck_remote_note_StringVar']
        )
        self.UIData['label_deck_remote_note_StringVar'].set(
            value = self.UIData['label_deck_remote_note_StringVar_origin']
        )
        self.UIObject['label_deck_remote_note'].configure(
            bg = self.UIConfig['color_001'],
            fg = self.UIConfig['color_004'],
            font = ('等线', 12)
        )
        self.UIObject['label_deck_remote_note'].grid(
            row = 0,
            column = 5,
            sticky = "nw",
            rowspan = 1,
            columnspan = 9,
            padx = (0, 0),
            pady = (10, 5),
            ipadx = 0,
            ipady = 0
        )

        self.UIObject['tree_deck_remote'] = ttk.Treeview(self.UIObject['frame_deck_root'])
        self.UIObject['tree_deck_remote']['show'] = 'headings'
        self.UIObject['tree_deck_remote']['columns'] = ('KEY', 'AUTHOR')
        self.UIObject['tree_deck_remote'].column('KEY', width = 35)
        self.UIObject['tree_deck_remote'].column('AUTHOR', width = 15)
        self.UIObject['tree_deck_remote'].heading('KEY', text = '牌堆名')
        self.UIObject['tree_deck_remote'].heading('AUTHOR', text = '作者')
        self.UIObject['tree_deck_remote'].grid(
            row = 1,
            column = 5,
            sticky = "nsew",
            rowspan = tmp_tree_rowspan,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )
        #self.UIObject['tree_rightkey_menu'] = tkinter.Menu(self.UIObject['root'], tearoff = False)
        #self.UIObject['tree_master'].bind('<Button-3>', lambda x : self.tree_master_rightKey(x))
        self.UIObject['tree_deck_remote'].bind('<<TreeviewSelect>>', lambda x : self.treeSelect('tree_deck_remote', x))
        self.UIObject['tree_deck_remote_yscroll'] = ttk.Scrollbar(
            self.UIObject['frame_deck_root'],
            orient = "vertical",
            command = self.UIObject['tree_deck_remote'].yview
        )
        self.UIObject['tree_deck_remote'].configure(
            yscrollcommand = self.UIObject['tree_deck_remote_yscroll'].set
        )
        self.UIObject['tree_deck_remote_yscroll'].grid(
            row = 1,
            column = 6,
            sticky = "nsw",
            rowspan = tmp_tree_rowspan,
            columnspan = 1,
            padx = (0, 0),
            pady = (0, 0),
            ipadx = 0,
            ipady = 0
        )

        self.UIData['label_deck_note_StringVar'] = tkinter.StringVar()
        self.UIObject['label_deck_note'] = tkinter.Text(
            self.UIObject['frame_deck_root'],
            wrap=tkinter.CHAR,
            width=30
        )
        self.UIObject['label_deck_note'].configure(
            bg = self.UIConfig['color_001'],
            fg = self.UIConfig['color_004'],
            bd = 0,
            font = ('等线', 11),
            padx = 4,
            pady = 8,
            state = tkinter.DISABLED,
            relief = tkinter.FLAT
        )
        self.UIObject['label_deck_note'].grid(
            row = 7,
            column = 2,
            sticky = "nswe",
            rowspan = 1,
            columnspan = 3,
            padx = (15, 15),
            pady = (20, 0),
            ipadx = 0,
            ipady = 0
        )

    def reload_deck_info(self):
        self.UIObject['label_deck_note'].configure(state=tkinter.NORMAL)
        tmp_dataList = OlivaDiceOdyssey.webTool.gExtiverseDeck
        tmp_deckName = self.UIData['deck_remote_now']
        self.UIObject['label_deck_note'].delete('1.0', tkinter.END)
        for deck_type_this in ['classic', 'yaml', 'excel']:
            if type(tmp_dataList) is dict \
            and deck_type_this in tmp_dataList \
            and type(tmp_dataList[deck_type_this]) is list:
                for deck_this in tmp_dataList[deck_type_this]:
                    if 'name' in deck_this \
                    and 'desc' in deck_this \
                    and 'version' in deck_this \
                    and 'version_code' in deck_this \
                    and 'author' in deck_this \
                    and 'type' in deck_this \
                    and 'sub_type' in deck_this \
                    and deck_this['name'] == tmp_deckName:
                        tmp_text = '%s\n\n%s\n作者: %s\n版本: %s(%s)\n\n%s' % (
                            str(deck_this['name']),
                            str({
                                'classic': '青果系JSON',
                                'yaml': '塔系YAML',
                                'excel': '梨系Excel'
                            }.get(deck_this['sub_type'], '新型')
                            ) + str({
                                'deck': '牌堆',
                            }.get(deck_this['type'], '未知扩展')),
                            str(deck_this['author']),
                            str(deck_this['version']),
                            str(deck_this['version_code']),
                            str(deck_this['desc'])
                        )
                        self.UIObject['label_deck_note'].insert('1.0', tmp_text)
                        break
        self.UIObject['label_deck_note'].configure(state=tkinter.DISABLED)

    def reloadDeck_local_gen(self):
        def reloadDeck_local_fun():
            try:
                OlivaDiceCore.drawCard.reloadDeck()
            except:
                pass
            self.init_data_deck_local()
        return reloadDeck_local_fun

    def installDeck_gen(self, flagUnity = False):
        def installDeck_fun():
            botHash = 'unity'
            deckName = self.UIData['deck_remote_now']
            if flagUnity:
                botHash = 'unity'
            else:
                botHash = self.UIData['hash_now']
            try:
                OlivaDiceOdyssey.webTool.downloadExtiverseDeckRemote(
                    name = deckName,
                    botHash = botHash
                )
                OlivaDiceCore.drawCard.reloadDeck()
            except:
                pass
            self.init_data_deck_local()
        return installDeck_fun

    def removeDeck_gen(self):
        def removeDeck_fun():
            deckName = self.UIData['deck_local_now']
            botHash = self.UIData['hash_now']
            try:
                OlivaDiceCore.drawCard.removeDeck(
                    botHash = botHash,
                    deckName = deckName
                )
                OlivaDiceCore.drawCard.removeDeck(
                    botHash = 'unity',
                    deckName = deckName
                )
                OlivaDiceCore.drawCard.reloadDeck()
            except Exception as e:
                traceback.print_exc()
            self.init_data_deck_local()
        return removeDeck_fun

    def openDeckPath_gen(self, flagUnity = False):
        def openDeckPath_fun():
            botHash = 'unity'
            deckName = self.UIData['deck_remote_now']
            if flagUnity:
                botHash = 'unity'
            else:
                botHash = self.UIData['hash_now']
            deck_path = os.path.join('plugin', 'data', 'OlivaDice', botHash, 'extend')
            try:
                os.startfile(deck_path)
            except:
                pass
        return openDeckPath_fun

    def uploadDeckUrl_gen(self):
        def uploadDeckUrl_fun():
            self.show_project_site('https://github.com/OlivOS-Team/Extiverse')
        return uploadDeckUrl_fun

    def onNotebookTabChanged(self, event):
        curTab = self.UIObject['Notebook_root'].tab(self.UIObject['Notebook_root'].select(), "text")
        if curTab == '牌堆管理':
            self.init_data_deck_local()
            # 异步执行
            threading.Thread(target = self.onNotebookTabChanged_init_data_deck_remote).start()


    def onNotebookTabChanged_init_data_deck_remote(self):
        if not self.UIData['deck_remote_loaded_flag']:
            # 仅在第一次切过来时刷新
            self.UIData['deck_remote_loaded_flag'] = True
            self.UIData['label_deck_remote_note_StringVar'].set(
                value = self.UIData['label_deck_remote_note_StringVar_load']
            )
            # 可以考虑在网络操作前就进行一次清空
            #self.init_data_deck_remote_pre()
            try:
                OlivaDiceOdyssey.webTool.getExtiverseDeckRemote()
            except:
                self.UIData['label_deck_remote_note_StringVar'].set(
                    value = self.UIData['label_deck_remote_note_StringVar_failed']
                )
            self.init_data_deck_remote()
            self.UIData['label_deck_remote_note_StringVar'].set(
                value = self.UIData['label_deck_remote_note_StringVar_origin']
            )

    def treeSelect(self, name, x):
        if name == 'tree_master':
            force = get_tree_force(self.UIObject['tree_master'])
            self.UIData['entry_master_StringVar'].set(str(force['text']))
        if name == 'tree_deck_local':
            force = get_tree_force(self.UIObject['tree_deck_local'])
            self.UIData['deck_local_now'] = str(force['text'])
        if name == 'tree_deck_remote':
            force = get_tree_force(self.UIObject['tree_deck_remote'])
            self.UIData['deck_remote_now'] = str(force['text'])
            self.reload_deck_info()

    def tree_str_rightKey(self, event):
        self.UIObject['tree_rightkey_menu'].delete(0, tkinter.END)
        self.UIObject['tree_rightkey_menu'].add_command(label = '编辑', command = lambda : self.tree_str_edit())
        self.UIObject['tree_rightkey_menu'].add_command(label='恢复/删除', command=lambda: self.reset_selected_str())
        self.UIObject['tree_rightkey_menu'].post(event.x_root, event.y_root)

    def tree_console_rightKey(self, event):
        self.UIObject['tree_rightkey_menu'].delete(0, tkinter.END)
        self.UIObject['tree_rightkey_menu'].add_command(label = '编辑', command = lambda : self.tree_console_edit())
        self.UIObject['tree_rightkey_menu'].add_command(label='恢复/删除', command=lambda: self.reset_selected_console())
        self.UIObject['tree_rightkey_menu'].post(event.x_root, event.y_root)

    def tree_str_edit(self):
        tmp_key = get_tree_force(self.UIObject['tree_str'])['text']
        if len(tmp_key) > 0:
            self.edit_str_UI(
                root_obj = self.UIObject['root'],
                root_class = self,
                key = tmp_key,
                hash = self.UIData['hash_now']
            ).start()

    def tree_console_edit(self):
        tmp_key = get_tree_force(self.UIObject['tree_console'])['text']
        if len(tmp_key) > 0:
            self.edit_console_UI(
                root_obj = self.UIObject['root'],
                root_class = self,
                key = tmp_key,
                hash = self.UIData['hash_now']
            ).start()

    def tree_master_config(self, action:str):
        tmp_hashSelection = self.UIData['hash_now']
        tmp_platform = None
        if tmp_hashSelection in OlivaDiceNativeGUI.load.dictBotInfo:
            tmp_platform = OlivaDiceNativeGUI.load.dictBotInfo[tmp_hashSelection].platform['platform']
        tmp_master_target = self.UIData['entry_master_StringVar'].get()
        try:
            tmp_master_target = int(tmp_master_target)
        except:
            tmp_master_target = None
        if tmp_platform != None and tmp_master_target != None:
            tmp_master_target = str(tmp_master_target)
            if action == 'add':
                tmp_dataList_new = []
                tmp_dataList = OlivaDiceCore.console.getConsoleSwitchByHash(
                    'masterList',
                    tmp_hashSelection
                )
                flag_done = False
                for tmp_dataList_this in tmp_dataList:
                    if len(tmp_dataList_this) == 2:
                        if str(tmp_dataList_this[0]) == tmp_master_target:
                            flag_done = True
                        tmp_dataList_new.append(tmp_dataList_this)
                if not flag_done:
                    tmp_dataList_new.append(
                        [
                            tmp_master_target,
                            tmp_platform
                        ]
                    )
                    OlivaDiceCore.console.setConsoleSwitchByHash(
                        'masterList',
                        tmp_dataList_new,
                        tmp_hashSelection
                    )
                    OlivaDiceCore.console.saveConsoleSwitch()
                    self.init_data_total()
            elif action == 'del':
                tmp_dataList_new = []
                tmp_dataList = OlivaDiceCore.console.getConsoleSwitchByHash(
                    'masterList',
                    tmp_hashSelection
                )
                flag_done = False
                for tmp_dataList_this in tmp_dataList:
                    if len(tmp_dataList_this) == 2:
                        if str(tmp_dataList_this[0]) == tmp_master_target:
                            flag_done = True
                        else:
                            tmp_dataList_new.append(tmp_dataList_this)
                if flag_done:
                    OlivaDiceCore.console.setConsoleSwitchByHash(
                        'masterList',
                        tmp_dataList_new,
                        tmp_hashSelection
                    )
                    OlivaDiceCore.console.saveConsoleSwitch()
                    self.init_data_total()

    class edit_str_UI(object):
        def __init__(self, root_obj, root_class, key, hash):
            self.root = root_obj
            self.root_class = root_class
            self.key = key
            self.hash = hash
            self.data = None
            self.UIObject = {}
            self.UIData = {}
            self.UIConfig = {}
            self.UIConfig.update(dictColorContext)
            
        def start(self):
            self.UIObject['root'] = tkinter.Toplevel(self.root)
            self.UIObject['root'].title('修改设置 - %s' % self.key)
            self.UIObject['root'].geometry('400x300')
            self.UIObject['root'].minsize(400, 300)
            self.UIObject['root'].resizable(
                width = True,
                height = True
            )
            self.UIObject['root'].grid_rowconfigure(0, weight = 0)
            self.UIObject['root'].grid_rowconfigure(1, weight = 15)
            self.UIObject['root'].grid_columnconfigure(0, weight = 15)
            self.UIObject['root'].configure(bg = self.UIConfig['color_001'])

            dictStrCustomDict = OlivaDiceCore.msgCustom.dictStrCustomDict
            dictStrCustomNote = OlivaDiceNativeGUI.msgCustom.dictStrCustomNote

            tmp_info = '无说明'
            tmp_data = ''
            if self.key in dictStrCustomNote:
                tmp_info = dictStrCustomNote[self.key]
            if self.hash in dictStrCustomDict:
                if self.key in dictStrCustomDict[self.hash]:
                    tmp_data = dictStrCustomDict[self.hash][self.key]
            self.data = tmp_data

            self.UIObject['label_note'] = tkinter.Label(
                self.UIObject['root'],
                text = tmp_info,
                font = ('等线', 12, 'bold')
            )
            self.UIObject['label_note'].configure(
                bg = self.UIConfig['color_001'],
                fg = self.UIConfig['color_004'],
                justify = 'left',
                anchor = 'nw'
            )
            self.UIObject['label_note'].grid(
                row = 0,
                column = 0,
                sticky = "nsew",
                rowspan = 1,
                columnspan = 1,
                padx = (15, 15),
                pady = (15, 0),
                ipadx = 0,
                ipady = 0
            )
            self.UIData['entry_edit_StringVar'] = tkinter.StringVar()
            self.UIObject['entry_edit'] = tkinter.Text(
                self.UIObject['root'],
                wrap = tkinter.WORD
            )
            self.UIObject['entry_edit'].configure(
                bg = self.UIConfig['color_004'],
                fg = self.UIConfig['color_005'],
                bd = 0,
                font = (None, 10),
                padx = 4,
                pady = 8
            )
            self.UIObject['entry_edit'].grid(
                row = 1,
                column = 0,
                sticky = "nsew",
                rowspan = 1,
                columnspan = 1,
                padx = (15, 15),
                pady = (8, 15),
                ipadx = 4,
                ipady = 8
            )
            self.UIObject['entry_edit'].insert('1.0', tmp_data)

            self.UIObject['root'].iconbitmap('./resource/tmp_favoricon.ico')

            self.UIObject['root'].protocol("WM_DELETE_WINDOW", self.quit)

            self.UIObject['root'].mainloop()

        def quit(self):
            self.save()
            if self.root_class != None:
                self.root_class.init_data_total()
            self.UIObject['root'].destroy()

        def save(self):
            tmp_new_str = self.UIObject['entry_edit'].get('1.0', tkinter.END)[:-1]
            if self.data != None and tmp_new_str != self.data:
                OlivaDiceCore.msgCustom.dictStrCustomUpdateDict[self.hash][self.key] = tmp_new_str
                OlivaDiceCore.msgCustom.dictStrCustomDict[self.hash][self.key] = tmp_new_str
                OlivaDiceCore.msgCustomManager.saveMsgCustomByBotHash(self.hash)


    class edit_console_UI(object):
        def __init__(self, root_obj, root_class, key, hash):
            self.root = root_obj
            self.root_class = root_class
            self.key = key
            self.hash = hash
            self.data = None
            self.UIObject = {}
            self.UIData = {}
            self.UIConfig = {}
            self.UIConfig.update(dictColorContext)
            
        def start(self):
            self.UIObject['root'] = tkinter.Toplevel(self.root)
            self.UIObject['root'].title('修改设置 - %s' % self.key)
            #self.UIObject['root'].geometry('400x100')
            self.UIObject['root'].minsize(400, 10)
            self.UIObject['root'].resizable(
                width = True,
                height = False
            )
            self.UIObject['root'].grid_rowconfigure(0, weight = 0)
            self.UIObject['root'].grid_rowconfigure(1, weight = 15)
            self.UIObject['root'].grid_columnconfigure(0, weight = 15)
            self.UIObject['root'].configure(bg = self.UIConfig['color_001'])

            dictConsoleSwitch = OlivaDiceCore.console.dictConsoleSwitch
            dictConsoleSwitchNote = OlivaDiceNativeGUI.msgCustom.dictConsoleSwitchNote

            tmp_info = '无说明'
            tmp_data = ''
            if self.key in dictConsoleSwitchNote:
                tmp_info = dictConsoleSwitchNote[self.key]
            if self.hash in dictConsoleSwitch:
                if self.key in dictConsoleSwitch[self.hash]:
                    tmp_data = dictConsoleSwitch[self.hash][self.key]
            self.data = tmp_data

            self.UIObject['label_note'] = tkinter.Label(
                self.UIObject['root'],
                text = tmp_info,
                font = ('等线', 12, 'bold')
            )
            self.UIObject['label_note'].configure(
                bg = self.UIConfig['color_001'],
                fg = self.UIConfig['color_004'],
                justify = 'left',
                anchor = 'nw'
            )
            self.UIObject['label_note'].grid(
                row = 0,
                column = 0,
                sticky = "nsew",
                rowspan = 1,
                columnspan = 1,
                padx = (15, 15),
                pady = (15, 0),
                ipadx = 0,
                ipady = 0
            )
            self.UIData['entry_edit_StringVar'] = tkinter.StringVar()
            self.UIObject['entry_edit'] = tkinter.Entry(
                self.UIObject['root'],
                textvariable = self.UIData['entry_edit_StringVar']
            )
            self.UIObject['entry_edit'].configure(
                bg = self.UIConfig['color_006'],
                fg = self.UIConfig['color_001'],
                bd = 0,
                font = ('等线', 12, 'bold'),
                justify = 'center'
                #width = width
            )
            self.UIObject['entry_edit'].grid(
                row = 1,
                column = 0,
                sticky = "n",
                rowspan = 1,
                columnspan = 1,
                padx = (15, 15),
                pady = (8, 15),
                ipadx = 0,
                ipady = 8
            )
            self.UIData['entry_edit_StringVar'].set(tmp_data)

            self.UIObject['root'].iconbitmap('./resource/tmp_favoricon.ico')

            self.UIObject['root'].protocol("WM_DELETE_WINDOW", self.quit)

            self.UIObject['root'].mainloop()

        def quit(self):
            self.save()
            if self.root_class != None:
                self.root_class.init_data_total()
            self.UIObject['root'].destroy()

        def save(self):
            tmp_new_str = self.UIData['entry_edit_StringVar'].get()
            if self.data != None and tmp_new_str != self.data:
                try:
                    OlivaDiceCore.console.dictConsoleSwitch[self.hash][self.key] = int(tmp_new_str)
                    OlivaDiceCore.console.saveConsoleSwitch()
                except:
                    pass

    def init_data_total(self):
        tmp_hashSelection = self.UIData['hash_now']
        # 全局模式禁用回复词里的所有按钮
        is_global_mode = (tmp_hashSelection == 'unity')
        if is_global_mode:
            for button_name in ['buttom_reset_str', 'buttom_import_str', 'buttom_export_str', 
                               'buttom_refresh_str', 'buttom_reset_delete_str']:
                if button_name in self.UIObject:
                    self.UIObject[button_name].config(state=tkinter.DISABLED)
        else:
            for button_name in ['buttom_reset_str', 'buttom_import_str', 'buttom_export_str', 
                               'buttom_refresh_str', 'buttom_reset_delete_str']:
                if button_name in self.UIObject:
                    self.UIObject[button_name].config(state=tkinter.NORMAL)

        self.UIData['onlineStatus_Label_root_StringVar'].set('当前在线: %s' % OlivaDiceNativeGUI.load.onlineAPICount)

        tmp_tree_item_children = self.UIObject['tree_str'].get_children()
        for tmp_tree_item_this in tmp_tree_item_children:
            self.UIObject['tree_str'].delete(tmp_tree_item_this)
        if tmp_hashSelection in OlivaDiceCore.msgCustom.dictStrCustomDict:
            tmp_dictStrCustomDict = OlivaDiceCore.msgCustom.dictStrCustomDict[tmp_hashSelection]
            for tmp_dictCustomData_this in OlivaDiceCore.msgCustom.dictStrCustomDict[tmp_hashSelection]:
                try:
                    tmp_value = tmp_dictStrCustomDict[tmp_dictCustomData_this]
                    tmp_value = tmp_value.replace('\r\n', r'\r\n')
                    tmp_value = tmp_value.replace('\n', r'\n')
                    tmp_value = tmp_value.replace('\r', r'\r')
                    tmp_note = ''
                    if tmp_dictCustomData_this in OlivaDiceNativeGUI.msgCustom.dictStrCustomNote:
                        tmp_note = OlivaDiceNativeGUI.msgCustom.dictStrCustomNote[tmp_dictCustomData_this]
                    tmp_note = tmp_note.replace('\n', ' ')
                    tmp_note = tmp_note.replace('\r', ' ')
                    self.UIObject['tree_str'].insert(
                        '',
                        tkinter.END,
                        text = tmp_dictCustomData_this,
                        values=(
                            tmp_dictCustomData_this,
                            tmp_note,
                            tmp_value
                        )
                    )
                except:
                    pass

        tmp_tree_item_children = self.UIObject['tree_console'].get_children()
        for tmp_tree_item_this in tmp_tree_item_children:
            self.UIObject['tree_console'].delete(tmp_tree_item_this)
        if tmp_hashSelection in OlivaDiceCore.console.dictConsoleSwitch:
            tmp_dictConsoleSwitch = OlivaDiceCore.console.dictConsoleSwitch[tmp_hashSelection]
            for tmp_dictConsoleSwitch_this in tmp_dictConsoleSwitch:
                try:
                    if type(tmp_dictConsoleSwitch[tmp_dictConsoleSwitch_this]) == int:
                        tmp_value = str(tmp_dictConsoleSwitch[tmp_dictConsoleSwitch_this])
                        tmp_value = tmp_value.replace('\r\n', r'\r\n')
                        tmp_value = tmp_value.replace('\n', r'\n')
                        tmp_value = tmp_value.replace('\r', r'\r')
                        tmp_note = ''
                        if tmp_dictConsoleSwitch_this in OlivaDiceNativeGUI.msgCustom.dictConsoleSwitchNote:
                            tmp_note = OlivaDiceNativeGUI.msgCustom.dictConsoleSwitchNote[tmp_dictConsoleSwitch_this]
                        tmp_note = tmp_note.replace('\n', ' ')
                        tmp_note = tmp_note.replace('\r', ' ')
                        self.UIObject['tree_console'].insert(
                            '',
                            tkinter.END,
                            text = tmp_dictConsoleSwitch_this,
                            values=(
                                tmp_dictConsoleSwitch_this,
                                tmp_note,
                                tmp_value
                            )
                        )
                except:
                    pass

        tmp_tree_item_children = self.UIObject['tree_master'].get_children()
        for tmp_tree_item_this in tmp_tree_item_children:
            self.UIObject['tree_master'].delete(tmp_tree_item_this)
        tmp_dataList = OlivaDiceCore.console.getConsoleSwitchByHash(
            'masterList',
            tmp_hashSelection
        )
        for tmp_dataList_this in tmp_dataList:
            if len(tmp_dataList_this) == 2:
                tmp_userName = '骰主'
                tmp_userRawId = tmp_dataList_this[0]
                tmp_userPlatform = tmp_dataList_this[1]
                tmp_botHash = tmp_hashSelection
                tmp_userHash = OlivaDiceCore.userConfig.getUserHash(
                    userId = tmp_userRawId,
                    userType = 'user',
                    platform = tmp_userPlatform
                )
                tmp_userId = OlivaDiceCore.userConfig.getUserDataByKeyWithHash(
                    userHash = tmp_userHash,
                    userDataKey = 'userId',
                    botHash = tmp_botHash
                )
                if tmp_userId != None:
                    tmp_userName = OlivaDiceCore.userConfig.getUserConfigByKeyWithHash(
                        userHash = tmp_userHash,
                        userConfigKey = 'userName',
                        botHash = tmp_botHash
                    )
                try:
                    self.UIObject['tree_master'].insert(
                        '',
                        tkinter.END,
                        text = str(tmp_dataList_this[0]),
                        values=(
                            str(tmp_dataList_this[0]),
                            str(tmp_userName)
                        )
                    )
                except:
                    pass
        self.init_data_deck_local()


    def init_data_deck(self):
        self.init_data_deck_local()

    def init_data_deck_local(self):
        tmp_hashSelection = self.UIData['hash_now']

        self.UIData['deck_local_now'] = None
        tmp_tree_item_children = self.UIObject['tree_deck_local'].get_children()
        for tmp_tree_item_this in tmp_tree_item_children:
            self.UIObject['tree_deck_local'].delete(tmp_tree_item_this)
        tmp_dataList = OlivaDiceCore.drawCardData.dictDeckIndex
        if tmp_hashSelection in tmp_dataList and type(tmp_dataList[tmp_hashSelection]) is dict:
            for deckName_this in tmp_dataList[tmp_hashSelection]:
                try:
                    self.UIObject['tree_deck_local'].insert(
                        '',
                        tkinter.END,
                        text = deckName_this,
                        values=(
                            deckName_this
                        )
                    )
                except:
                    pass


    def init_data_deck_remote_pre(self):
        tmp_hashSelection = self.UIData['hash_now']

        self.UIData['deck_remote_now'] = None
        tmp_tree_item_children = self.UIObject['tree_deck_remote'].get_children()
        for tmp_tree_item_this in tmp_tree_item_children:
            self.UIObject['tree_deck_remote'].delete(tmp_tree_item_this)

    def init_data_deck_remote(self):
        tmp_hashSelection = self.UIData['hash_now']

        self.UIData['deck_remote_now'] = None
        tmp_tree_item_children = self.UIObject['tree_deck_remote'].get_children()
        for tmp_tree_item_this in tmp_tree_item_children:
            self.UIObject['tree_deck_remote'].delete(tmp_tree_item_this)
        tmp_dataList = OlivaDiceOdyssey.webTool.gExtiverseDeck
        for deck_type_this in ['classic', 'yaml', 'excel']:
            if type(tmp_dataList) is dict \
            and deck_type_this in tmp_dataList \
            and type(tmp_dataList[deck_type_this]) is list:
                for deck_this in tmp_dataList[deck_type_this]:
                    if 'name' in deck_this \
                    and 'author' in deck_this:
                        deckName_this = deck_this['name']
                        deckAuthor_this = deck_this['author']
                        try:
                            self.UIObject['tree_deck_remote'].insert(
                                '',
                                tkinter.END,
                                text = deckName_this,
                                values=(
                                    deckName_this,
                                    deckAuthor_this
                                )
                            )
                        except:
                            pass
                        
    def reset_str_confirm(self):
        """显示恢复默认回复词的确认对话框"""
        if tkinter.messagebox.askyesno(
            "确认恢复",
            "确定要恢复所有回复词为默认值吗？这将删除所有自定义回复词。",
            parent=self.UIObject['root']
        ):
            self.reset_str_default()

    def reset_str_default(self):
        """实际执行恢复默认回复词的操作"""
        tmp_hashSelection = self.UIData['hash_now']
        if tmp_hashSelection in OlivaDiceCore.msgCustom.dictStrCustomDict:
            OlivaDiceCore.msgCustom.dictStrCustomDict[tmp_hashSelection] = self.default_reply_config().copy()
            OlivaDiceCore.msgCustom.dictStrCustomUpdateDict[tmp_hashSelection] = {}
            OlivaDiceCore.msgCustomManager.saveMsgCustomByBotHash(tmp_hashSelection)
            self.init_data_total()
            tkinter.messagebox.showinfo("完成", "已恢复所有回复词为默认值", parent=self.UIObject['root'])

    def reset_console_confirm(self):
        """显示恢复默认配置的确认对话框"""
        if tkinter.messagebox.askyesno(
            "确认恢复",
            "确定要恢复所有配置项为默认值吗？这将重置所有自定义配置。",
            parent=self.UIObject['root']
        ):
            self.reset_console_default()

    def reset_console_default(self):
        """实际执行恢复默认配置的操作"""
        tmp_hashSelection = self.UIData['hash_now']
        if tmp_hashSelection in OlivaDiceCore.console.dictConsoleSwitch:
            # masterList不换
            current_master_list = OlivaDiceCore.console.dictConsoleSwitch[tmp_hashSelection].get('masterList', [])
            default_config = OlivaDiceCore.console.dictConsoleSwitchTemplate['default'].copy()
            OlivaDiceCore.console.dictConsoleSwitch[tmp_hashSelection] = default_config
            OlivaDiceCore.console.dictConsoleSwitch[tmp_hashSelection]['masterList'] = current_master_list
            OlivaDiceCore.console.saveConsoleSwitch()
            self.init_data_total()
            tkinter.messagebox.showinfo("完成", "已恢复所有配置项为默认值", parent=self.UIObject['root'])

    def reset_selected_str(self):
        """恢复或删除选中的回复词"""
        tmp_key = get_tree_force(self.UIObject['tree_str'])['text']
        if not tmp_key:
            tkinter.messagebox.showwarning("警告", "请先选择要操作的回复词", parent=self.UIObject['root'])
            return

        tmp_hashSelection = self.UIData['hash_now']
        current_str_dict = OlivaDiceCore.msgCustom.dictStrCustomDict.get(tmp_hashSelection, {})
        default_str_dict = self.default_reply_config_for_delete().copy()

        if tmp_key in default_str_dict:
            if tkinter.messagebox.askyesno(
                "确认恢复",
                f"确定要恢复'{tmp_key}'的回复词为默认值吗？",
                parent=self.UIObject['root']
            ):
                default_value = default_str_dict[tmp_key]
                current_str_dict[tmp_key] = default_value
                OlivaDiceCore.msgCustom.dictStrCustomDict[tmp_hashSelection] = current_str_dict
                if tmp_hashSelection in OlivaDiceCore.msgCustom.dictStrCustomUpdateDict:
                    if tmp_key in OlivaDiceCore.msgCustom.dictStrCustomUpdateDict[tmp_hashSelection]:
                        del OlivaDiceCore.msgCustom.dictStrCustomUpdateDict[tmp_hashSelection][tmp_key]
                OlivaDiceCore.msgCustomManager.saveMsgCustomByBotHash(tmp_hashSelection)
                self.init_data_total()
        else:
            if tkinter.messagebox.askyesno(
                "确认删除",
                f"确定要删除'{tmp_key}'的自定义回复词吗？",
                parent=self.UIObject['root']
            ):
                if tmp_key in current_str_dict:
                    del current_str_dict[tmp_key]
                    OlivaDiceCore.msgCustom.dictStrCustomDict[tmp_hashSelection] = current_str_dict
                    
                if tmp_hashSelection in OlivaDiceCore.msgCustom.dictStrCustomUpdateDict:
                    if tmp_key in OlivaDiceCore.msgCustom.dictStrCustomUpdateDict[tmp_hashSelection]:
                        del OlivaDiceCore.msgCustom.dictStrCustomUpdateDict[tmp_hashSelection][tmp_key]
                        
                OlivaDiceCore.msgCustomManager.saveMsgCustomByBotHash(tmp_hashSelection)
                self.init_data_total()

    def reset_selected_console(self):
        """恢复选中的配置项为默认值"""
        tmp_key = get_tree_force(self.UIObject['tree_console'])['text']
        if not tmp_key:
            tkinter.messagebox.showwarning("警告", "请先选择要操作的配置项", parent=self.UIObject['root'])
            return

        tmp_hashSelection = self.UIData['hash_now']
        default_config = OlivaDiceCore.console.dictConsoleSwitchTemplate['default']
        current_console_dict = OlivaDiceCore.console.dictConsoleSwitch.get(tmp_hashSelection, {})

        if tmp_key in default_config:
            if tkinter.messagebox.askyesno(
                "确认恢复",
                f"确定要恢复'{tmp_key}'的配置为默认值吗？",
                parent=self.UIObject['root']
            ):
                if isinstance(default_config[tmp_key], list):
                    current_console_dict[tmp_key] = default_config[tmp_key].copy()
                else:
                    current_console_dict[tmp_key] = default_config[tmp_key]
                    
                OlivaDiceCore.console.dictConsoleSwitch[tmp_hashSelection] = current_console_dict
                OlivaDiceCore.console.saveConsoleSwitch()
                self.init_data_total()
        else:
            if tkinter.messagebox.askyesno(
                "确认删除",
                f"确定要删除'{tmp_key}'的自定义配置吗？",
                parent=self.UIObject['root']
            ):
                if tmp_key in current_console_dict:
                    del current_console_dict[tmp_key]
                    OlivaDiceCore.console.dictConsoleSwitch[tmp_hashSelection] = current_console_dict
                    OlivaDiceCore.console.saveConsoleSwitch()
                    self.init_data_total()

    def import_str_config(self):
        """导入回复词配置"""
        file_path = tkinter.filedialog.askopenfilename(
            title="选择回复词配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            parent=self.UIObject['root']
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                if not isinstance(import_data, dict):
                    raise ValueError("配置文件格式不正确，必须是一个JSON文件")
                if tkinter.messagebox.askyesno(
                    "确认导入",
                    f"确定要导入回复词配置吗？这将覆盖当前配置。",
                    parent=self.UIObject['root']
                ):
                    tmp_hashSelection = self.UIData['hash_now']
                    backup_data = OlivaDiceCore.msgCustom.dictStrCustomDict.get(tmp_hashSelection, {}).copy()
                    backup_update = OlivaDiceCore.msgCustom.dictStrCustomUpdateDict.get(tmp_hashSelection, {}).copy()
                    try:
                        # 覆盖导入
                        current_data = OlivaDiceCore.msgCustom.dictStrCustomDict.get(tmp_hashSelection, {})
                        current_update = OlivaDiceCore.msgCustom.dictStrCustomUpdateDict.get(tmp_hashSelection, {})
                        updated_data = current_data.copy()
                        updated_data.update(import_data)
                        updated_update = current_update.copy()
                        updated_update.update(import_data)
                        OlivaDiceCore.msgCustom.dictStrCustomDict[tmp_hashSelection] = updated_data
                        OlivaDiceCore.msgCustom.dictStrCustomUpdateDict[tmp_hashSelection] = updated_update
                        OlivaDiceCore.msgCustomManager.saveMsgCustomByBotHash(tmp_hashSelection)
                        self.init_data_total()
                        tkinter.messagebox.showinfo("完成", "回复词配置导入成功", parent=self.UIObject['root'])
                    except Exception as e:
                        OlivaDiceCore.msgCustom.dictStrCustomDict[tmp_hashSelection] = backup_data
                        OlivaDiceCore.msgCustom.dictStrCustomUpdateDict[tmp_hashSelection] = backup_update
                        self.init_data_total()
                        raise
            except Exception as e:
                tkinter.messagebox.showerror("错误", f"导入失败: {str(e)}\n配置未更改", parent=self.UIObject['root'])

    def export_str_config(self):
        """导出回复词配置"""
        file_path = tkinter.filedialog.asksaveasfilename(
            title="保存回复词配置文件",
            defaultextension=".json",
            initialfile="customReply.json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            parent=self.UIObject['root']
        )
        if file_path:
            try:
                tmp_hashSelection = self.UIData['hash_now']
                export_data = OlivaDiceCore.msgCustom.dictStrCustomDict.get(tmp_hashSelection, {})
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=4)
                tkinter.messagebox.showinfo("完成", "回复词配置导出成功", parent=self.UIObject['root'])
            except Exception as e:
                tkinter.messagebox.showerror("错误", f"导出失败: {str(e)}", parent=self.UIObject['root'])

    def refresh_str_config(self):
        """刷新回复词配置"""
        if tkinter.messagebox.askyesno(
            "确认刷新",
            "确定要从文件重新加载回复词配置吗？这将覆盖当前所有修改。",
            parent=self.UIObject['root']
        ):
            tmp_hashSelection = self.UIData['hash_now']
            default_reply = self.default_reply_config()
            backup_data = OlivaDiceCore.msgCustom.dictStrCustomDict.get(tmp_hashSelection, {}).copy()
            backup_update = OlivaDiceCore.msgCustom.dictStrCustomUpdateDict.get(tmp_hashSelection, {}).copy()
            try:
                OlivaDiceCore.msgCustom.dictStrCustomDict[tmp_hashSelection] = default_reply.copy()
                customReplyDir = OlivaDiceCore.data.dataDirRoot + '/' + tmp_hashSelection + '/console'
                customReplyFile = 'customReply.json'
                customReplyPath = customReplyDir + '/' + customReplyFile

                try:
                    with open(customReplyPath, 'r', encoding='utf-8') as customReplyPath_f:
                        update_data = json.load(customReplyPath_f)
                        if not isinstance(update_data, dict):
                            raise ValueError("自定义回复文件格式不正确")

                        OlivaDiceCore.msgCustom.dictStrCustomUpdateDict[tmp_hashSelection] = update_data
                        OlivaDiceCore.msgCustom.dictStrCustomDict[tmp_hashSelection].update(update_data)
                except FileNotFoundError:
                    pass
                except Exception as e:
                    raise ValueError(f"读取自定义回复文件失败: {str(e)}")

                self.init_data_total()
                tkinter.messagebox.showinfo("完成", "回复词配置刷新成功", parent=self.UIObject['root'])
            except Exception as e:
                OlivaDiceCore.msgCustom.dictStrCustomDict[tmp_hashSelection] = backup_data
                OlivaDiceCore.msgCustom.dictStrCustomUpdateDict[tmp_hashSelection] = backup_update
                tkinter.messagebox.showerror("错误", f"刷新失败: {str(e)}\n配置未更改", parent=self.UIObject['root'])

    def import_console_config(self):
        """导入控制台配置"""
        file_path = tkinter.filedialog.askopenfilename(
            title="选择控制台配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            parent=self.UIObject['root']
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)

                if not isinstance(import_data, dict):
                    raise ValueError("配置文件格式不正确，必须是一个JSON文件")

                if tkinter.messagebox.askyesno(
                    "确认导入",
                    f"确定要导入控制台配置吗？这将覆盖当前配置。",
                    parent=self.UIObject['root']
                ):
                    tmp_hashSelection = self.UIData['hash_now']
                    current_config = OlivaDiceCore.console.dictConsoleSwitch.get(tmp_hashSelection, {})
                    backup_data = current_config.copy()
                    try:
                        for key in import_data:
                            current_config[key] = import_data[key]
                        OlivaDiceCore.console.dictConsoleSwitch[tmp_hashSelection] = current_config
                        OlivaDiceCore.console.saveConsoleSwitch()
                        self.init_data_total()
                        tkinter.messagebox.showinfo("完成", "控制台配置导入成功", parent=self.UIObject['root'])
                    except Exception as e:
                        OlivaDiceCore.console.dictConsoleSwitch[tmp_hashSelection] = backup_data
                        OlivaDiceCore.console.saveConsoleSwitch()
                        self.init_data_total()
                        raise
            except Exception as e:
                tkinter.messagebox.showerror("错误", f"导入失败: {str(e)}\n配置未更改", parent=self.UIObject['root'])

    def export_console_config(self):
        """导出控制台配置"""
        file_path = tkinter.filedialog.asksaveasfilename(
            title="保存控制台配置文件",
            defaultextension=".json",
            initialfile="switch.json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            parent=self.UIObject['root']
        )
        if file_path:
            try:
                tmp_hashSelection = self.UIData['hash_now']
                export_data = OlivaDiceCore.console.dictConsoleSwitch.get(tmp_hashSelection, {})
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=4)
                tkinter.messagebox.showinfo("完成", "控制台配置导出成功", parent=self.UIObject['root'])
            except Exception as e:
                tkinter.messagebox.showerror("错误", f"导出失败: {str(e)}", parent=self.UIObject['root'])

    def refresh_console_config(self):
        """刷新控制台配置"""
        if tkinter.messagebox.askyesno(
            "确认刷新",
            "确定要从文件重新加载控制台配置吗？这将覆盖当前所有修改。",
            parent=self.UIObject['root']
        ):
            tmp_hashSelection = self.UIData['hash_now']
            backup_data = OlivaDiceCore.console.dictConsoleSwitch.get(tmp_hashSelection, {}).copy()
            try:
                default_config = OlivaDiceCore.console.dictConsoleSwitchTemplate['default'].copy()
                custom_config = {}
                config_dir = OlivaDiceCore.data.dataDirRoot + '/' + tmp_hashSelection + '/console'
                config_file = 'switch.json'
                config_path = config_dir + '/' + config_file
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        custom_config = json.load(f)
                        if not isinstance(custom_config, dict):
                            raise ValueError("配置文件格式不正确")
                except FileNotFoundError:
                    pass
                except Exception as e:
                    raise ValueError(f"读取配置文件失败: {str(e)}")
                merged_config = default_config.copy()
                merged_config.update(custom_config)
                if 'masterList' in backup_data:
                    merged_config['masterList'] = backup_data['masterList']
                OlivaDiceCore.console.dictConsoleSwitch[tmp_hashSelection] = merged_config
                OlivaDiceCore.console.saveConsoleSwitch()
                self.init_data_total()
                tkinter.messagebox.showinfo("完成", "控制台配置刷新成功", parent=self.UIObject['root'])
            except Exception as e:
                OlivaDiceCore.console.dictConsoleSwitch[tmp_hashSelection] = backup_data
                tkinter.messagebox.showerror("错误", f"刷新失败: {str(e)}\n配置未更改", parent=self.UIObject['root'])
    
    def default_reply_config(self):
        '''导入所有的dictStrCustom'''
        # 获取当前内存中的回复词配置
        tmp_hashSelection = self.UIData['hash_now']
        current_config = OlivaDiceCore.msgCustom.dictStrCustomDict.get(tmp_hashSelection, {}).copy()
        default_reply = OlivaDiceCore.msgCustom.dictStrCustom.copy()
        import_list = ['OlivaDiceJoy', 'OlivaDiceMaster', 'OlivaDiceLogger', 'OlivaDiceOdyssey', 'OlivaStoryCore']
        for module_name in import_list:
            try:
                module = importlib.import_module(module_name)
                default_reply.update(module.msgCustom.dictStrCustom)
            except:
                continue
        default_reply.update(OlivaDiceNativeGUI.msgCustom.dictStrCustom)
        merged_config = current_config.copy()
        for key in default_reply:
            merged_config[key] = default_reply[key]

        return merged_config

    def default_reply_config_for_delete(self):
        '''导入所有的dictStrCustom-删除用'''
        default_reply = OlivaDiceCore.msgCustom.dictStrCustom.copy()
        import_list = ['OlivaDiceJoy', 'OlivaDiceMaster', 'OlivaDiceLogger', 'OlivaDiceOdyssey', 'OlivaStoryCore']
        for module_name in import_list:
            try:
                module = importlib.import_module(module_name)
                default_reply.update(module.msgCustom.dictStrCustom)
            except:
                continue
        default_reply.update(OlivaDiceNativeGUI.msgCustom.dictStrCustom)
        return default_reply