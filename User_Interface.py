import tkinter as tk
import pandas as pd
from Pseudorandom_seq import Pseudorandom
import os
import datetime
import tkinter.font as tkFont
import tkinter.messagebox


# 暂存用户信息的字典
column_items = ['name', 'gender', 'age', 'fatigue', 'consistent',
                'hit', 'mistake', 'miss', 'hit_ratio', 'mistake_ratio',
                'react_time', 'setting', 'date']
user_data = {key: [] for key in column_items}

# 默认参数列表
default_param = [(2, 2, 30), (2, 1.5, 30), (2, 1, 30), (3, 2, 30), (3, 1.5, 30)]
c = 1
# speak = win.Dispatch("SAPI.SpVoice")


def num_refresh():
    """开始按下后的必要操作，开始报数，创建回应按键，记下命中、操作、反应时长等数据，一轮结束后的询问保存"""
    set_button['state'] = tk.DISABLED  # 禁用设置和开始按钮
    start_button['state'] = tk.DISABLED
    origin_label.destroy()
    # 仅在报数开始后才创建回应键，若按建按下则调用序列本身的hit和mistake检查方法
    spark_button = tk.Button(window, text='Spark!', width=10, height=5, command=seq.check_hit_mistake)
    spark_button.place(relx=0.5, rely=0.8, width=100, height=50, anchor='center')
    spark_button['state'] = tk.DISABLED

    def refresh():
        """定时执行该模块"""
        if seq.dictate_count < seq.trials:
            """一轮报数开始后的必要操作"""
            number = seq.dictate()  # 调用dictate方法定时刷新序列当前数字
            num_var.set(number)
            label.place(anchor='center', relx=0.45, rely=0.35)
            window.after(int(seq.interval * 1000), refresh)
            if seq.dictate_count > seq.step:
                """n步报数后的按键检查才有意义"""
                spark_button['state'] = tk.NORMAL  # 仅在n步后才激活回应键
                window.bind("<space>", seq.check_hit_mistake)
                seq.consistent_cal()  # 一致计数
        else:
            """以下为一轮结束后的必要操作"""
            window.after_cancel(num_refresh)  # 定时结束
            label.place_forget()
            set_button['state'] = tk.NORMAL  # 重新启用开始和设置按钮
            start_button['state'] = tk.NORMAL
            spark_button['state'] = tk.DISABLED
            print('一致数:{}  命中数:{}  错误数{}  反应用时{}'.
                  format(seq.consistent, seq.hit, seq.mistake, sum(seq.react_time)))  # 统计数据
            append_quest()  # 询问是否添加此条数据
            param_get()  # 重新获取序列参数以开始新一轮试验
    refresh()


def append_quest():
    """在一轮试验结束后询问是否添加本轮数据"""
    if tk.messagebox.askyesno(title='提示', message='是否添加该轮数据？'):
        consistent_info = seq.consistent
        hit_info = seq.hit
        mistake_info = seq.mistake
        miss_info = seq.consistent - seq.hit
        try:
            hit_ratio_info = hit_info / consistent_info
            mistake_ratio_info = mistake_info / (seq.trials - seq.step - consistent_info)
        except ZeroDivisionError:
            hit_ratio_info = 'NA'
            mistake_ratio_info = 'NA'
        react_time_info = sum(seq.react_time) + miss_info * seq.interval
        setting_info = (seq.step, seq.interval, seq.trials)
        date_info = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')  # 设定时间格式
        for key in column_items:
            user_data[key].append(eval(key + '_info'))
        print(pd.DataFrame(user_data))


def info_input():
    """在首次进入程序时创建顶层窗口强制录入用户信息，否则不让start开始试验"""
    user_info_quest = tk.Toplevel(window)
    user_info_quest.title('用户信息录入')
    user_info_quest.geometry('400x260')
    tk.Label(user_info_quest, text='Name').grid(row=0, column=0)
    tk.Label(user_info_quest, text='Age').grid(row=1, column=0)

    def info_get():
        """暂存用户信息，待试验结束统计完各项数据，将其一块保存为pd.DataFrame对象"""
        # 这四项信息作为主键
        global user_data, column_items, name_info, gender_info, age_info, fatigue_info
        name_info = name_entry.get()
        gender_info = gender_var.get()
        age_info = age_scale.get()
        fatigue_info = fatigue_var.get()
        user_info_quest.destroy()
        start_button['state'] = tk.NORMAL

    def info_clear():
        """清空信息栏"""
        name_entry.delete(0, tk.END)
        gender_var.set('male')
        age_scale.set(value=18)
        fatigue_var.set(0)

    # 姓名和年龄选项
    name_str = tk.StringVar()
    name_entry = tk.Entry(user_info_quest, width=12, textvariable=name_str)
    tip_label = tk.Label(user_info_quest, text='(请输入姓名全拼音)')
    tip_label.place(relx=0.08, rely=0.19)
    name_entry.grid(row=0, column=1, ipady=3)
    age_scale = tk.Scale(user_info_quest, from_=18, to=30, orient=tk.HORIZONTAL)
    age_scale.grid(row=1, column=1, ipady=3, pady=16)

    # 性别选项框
    gender_var = tk.StringVar()
    gender_var.set('male')
    gender_frame = tk.Frame(user_info_quest)
    tk.Label(gender_frame, text='Gender').pack(pady=3)
    tk.Radiobutton(gender_frame, text='男', value='male', variable=gender_var).pack(side='left')
    tk.Radiobutton(gender_frame, text='女', value='female', variable=gender_var).pack(side='left')
    gender_frame.grid(row=0, column=2, padx=20, pady=8)

    # 疲劳选项框
    fatigue_var = tk.IntVar()
    fatigue_var.set(0)
    fatigue_frame = tk.Frame(user_info_quest)
    tk.Label(fatigue_frame, text='Fatigue').pack(pady=3)
    tk.Radiobutton(fatigue_frame, text='清醒', value=0, variable=fatigue_var).pack(side='left')
    tk.Radiobutton(fatigue_frame, text='微疲劳', value=1, variable=fatigue_var).pack(side='left')
    tk.Radiobutton(fatigue_frame, text='很疲劳', value=2, variable=fatigue_var).pack(side='left')
    fatigue_frame.grid(row=1, column=2, padx=20, pady=16)

    # 信息确认键
    confirm_button = tk.Button(user_info_quest, text='OK', command=info_get)
    confirm_button.place(relx=0.22, rely=0.8, width=100, height=50)
    # 信息清除键
    clear_button = tk.Button(user_info_quest, text='Clear', command=info_clear)
    clear_button.place(relx=0.52, rely=0.8, width=100, height=50)
    user_info_quest.mainloop()


def quit_quest():
    """退出时询问是否保存"""
    quit_flag = tk.messagebox.askyesno(title='提示', message='是否保存？')
    if quit_flag:
        frame = pd.DataFrame(user_data)
        frame.to_csv('user_data/'+str(name_info)+'.csv')
    window.destroy()


def param_get():
    """"一轮报数前设定步长N,interval和trial等参数，若不触发此事件则使用默认值"""
    global seq
    # 每次调用该函数都会重新初始化一个从Entry处获得参数的新的N back序列
    seq = Pseudorandom(int(N_entry.get()), float(interval_entry.get()), int(trials_entry.get()))


def author_intro():
    """点击进入关于作者的txt文件说明"""
    os.startfile('about author.txt')


def n_back_intro():
    """点击进入关于N back的游戏说明txt说明"""
    os.startfile('about N_back.txt')


def open_dir():
    """打开数据存储文件夹"""
    os.startfile('user_data')


def current_visible():
    """创建数字队列可见区域"""
    pass


def performance_visible():
    """创建统计数据可见区域"""


def switch_param():
    """轮换默认参数组"""
    global N_default, interval_default, trials_default, c
    if c < 5:
        value = default_param[c]
        c += 1
    else:
        value = default_param[0]
        c = 1
    N_default.set(value[0])
    interval_default.set(value[1])
    trials_default.set(value[2])
    param_get()


# 主界面窗口
window = tk.Tk()
window.title('N_ back trial')
window.geometry('400x260')


# 顶部菜单功能区，包含开始，保存，退出等选项
menu_bar = tk.Menu(window)
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label='File', menu=file_menu)
file_menu.add_command(label='Info Input', command=info_input)
file_menu.add_command(label='Start', command=num_refresh)
file_menu.add_command(label='save', command=append_quest)
file_menu.add_separator()
file_menu.add_command(label='exit', command=quit_quest)
edit_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label='Help', menu=edit_menu)
edit_menu.add_command(label='about N back', command=n_back_intro)
edit_menu.add_command(label='about author', command=author_intro)
sub_menu = tk.Menu(file_menu)
file_menu.add_cascade(label='View', menu=sub_menu, underline=0)
sub_menu.add_command(label='data folder', command=open_dir)
sub_menu.add_command(label='current visible', command=None)
sub_menu.add_command(label='performance visible', command=None)
window.config(menu=menu_bar)


# 设置框，包含步长N，间隔interval,和试验次数trials
frame_settings = tk.Frame(window, width=150, height=130)
frame_settings.place(anchor='ne', relx=0.98, rely=0.10)
tk.Label(frame_settings, text='N').grid(row=0, column=0)
tk.Label(frame_settings, text='interval').grid(row=1, column=0)
tk.Label(frame_settings, text='trials').grid(row=2, column=0)
tk.Label(frame_settings, text='step').grid(row=0, column=2)
tk.Label(frame_settings, text='sec').grid(row=1, column=2)
tk.Label(frame_settings, text='times').grid(row=2, column=2)

# 设置默认值
N_default = tk.IntVar(window)
N_default.set(default_param[0][0])
interval_default = tk.IntVar(window)
interval_default.set(default_param[0][1])
trials_default = tk.IntVar(window)
trials_default.set(default_param[0][2])
# 参数设置Entry
N_entry = tk.Entry(frame_settings, width=10, textvariable=N_default)
N_entry.grid(row=0, column=1, ipady=3, pady=3)
interval_entry = tk.Entry(frame_settings, width=10, textvariable=interval_default)
interval_entry.grid(row=1, column=1, ipady=3, pady=3)
trials_entry = tk.Entry(frame_settings, width=10, textvariable=trials_default)
trials_entry.grid(row=2, column=1, ipady=3, pady=3)
# 设置键
set_button = tk.Button(frame_settings, text='config', command=param_get)
set_button.grid(row=3, column=2, pady=3)
# 切换键
switch_button = tk.Button(frame_settings, text='switch', command=switch_param)
switch_button.grid(row=3, column=1, pady=3)

# 信息录入键
info_button = tk.Button(window, text='input', width=10, height=3, command=info_input)
info_button.grid(row=0, column=0)
# 开始键
start_button = tk.Button(window, text='start', width=10, height=3, command=num_refresh)
start_button['state'] = tk.DISABLED
start_button.grid(row=1, column=0)

# 从Entry处得到参数生成N back序列
seq = Pseudorandom(int(N_entry.get()), float(interval_entry.get()), int(trials_entry.get()))

# 准备界面图片
ready_image = tk.PhotoImage(file='ready.png')
origin_label = tk.Label(window, image=ready_image)
origin_label.place(anchor='center', relx=0.4, rely=0.35)

# 数字Label
font = tkFont.Font(window, size=120)
num_var = tk.IntVar(window)
label = tk.Label(window, textvariable=num_var, font=font, relief='groove')
window.protocol('WM_DELETE_WINDOW', quit_quest)  # 窗口关闭保存请求
window.mainloop()
