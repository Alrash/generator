import tkinter as tk
from tkinter import ttk

import os
import re
import sys
import time

# init
maingui = tk.Tk()
maingui.title('界面')
maingui.geometry("800x500")
maingui.resizable(False, False)

# save function
def save_func(container):
    container.config(state = tk.DISABLED, background = 'LightGrey')
    txt = container.get('1.0', tk.END)[:-1]
    if len(txt) != 0:
        with open(time.strftime("generate#%Y-%m-%d_%H%M%S.txt", time.localtime()), 'w') as f:
            f.write(txt)
        print('save file successfully!')

# text container become writable
def writable_func(container):
    container.config(state = tk.NORMAL, background = 'white')

# append rect area
def append_func(container):
    father = tk.PanedWindow(container, orient = 'vertical', borderwidth = 1, relief = tk.SUNKEN)

    pw1 = tk.PanedWindow(father)
    pw2 = tk.PanedWindow(father, orient = 'vertical')

    # pw1
    tip = tk.Label(pw1, text = '区域重复次数:')
    entry = tk.Entry(pw1)
    fill1 = tk.Label(pw1, text = '  ')
    abtn = tk.Button(pw1, text = '增加规则', command = lambda: append_left_input(pw2))
    fill2 = tk.Label(pw1, text = '  ')
    dbtn = tk.Button(pw1, text = '移除区域', command = lambda: del_self_func(container, father))
    fill3 = tk.Label(pw1, text = '  ')

    entry.insert(0, '0,1,1')

    pw1.add(tip)
    pw1.add(entry)
    pw1.add(fill1)
    pw1.add(abtn)
    pw1.add(fill2)
    pw1.add(dbtn)
    pw1.add(fill3)

    # pw2
    append_left_input(pw2)

    father.add(pw1)
    father.add(pw2)

    container.add(father)

# append input in rect area
def append_left_input(container):
    items = tk.PanedWindow(container)
    
    rules = tk.Entry(items, width = 35)
    clm = tk.Entry(items, width = 5)
    row = tk.Entry(items, width = 5)
    del_btn = tk.Button(items, text = '删除', command = lambda: del_self_func(container, items))

    clm.insert(tk.INSERT, '1')
    row.insert(tk.INSERT, '1')

    items.add(rules, height = 1)
    items.add(clm)
    items.add(row)
    items.add(del_btn)
    
    container.add(items)

def del_self_func(container, child):
    container.remove(child)

def check_input(val: str, isrange = False, isrect = False):
    if isrect:
        return re.match(r'^(\d+,\d+,((\d+)|(l\d+c\d+)))$', val) is not None
    elif isrange:
        return re.match(r'^((\d+)|(l\d+c\d+))$', val) is not None
    else:
        return len(val) != 0

# write message to container
def write_msg(container, msg):
    container.config(state = tk.NORMAL, background = 'white')
    container.delete(1.0, tk.END)
    container.insert(1.0, msg)
    container.config(state = tk.DISABLED, background = 'LightGrey')


def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()


# generate data list and call generator command
def generate_func(parent, txt_container):
    data = []
    for rects in parent.panes():
        # get father panes
        rects_instance = parent.nametowidget(rects)
        rect_range_pane = rects_instance.nametowidget(rects_instance.panes()[0])
        rule_area_father_pane = rects_instance.nametowidget(rects_instance.panes()[1])

        # get rect range
        rect_range = rect_range_pane.nametowidget(rect_range_pane.panes()[1]).get().replace(' ', '')
        if not check_input(rect_range, isrect = True):
            write_msg(txt_container, '区域次数填写错误！\n仅支持"n,n,n"或者"n,n,lxcy"两种形式')
            return

        # get rules
        # tuple by list
        rules = []
        for item in rule_area_father_pane.panes():
            rule_area = rule_area_father_pane.nametowidget(item)

            rule_entry = rule_area.nametowidget(rule_area.panes()[0]).get().strip()
            if not check_input(rule_entry):
                write_msg(txt_container, '规则填写为空！')
                return

            col_entry = rule_area.nametowidget(rule_area.panes()[1]).get().replace(' ', '')
            row_entry = rule_area.nametowidget(rule_area.panes()[2]).get().replace(' ', '')
            if not check_input(col_entry, isrange = True) or not check_input(row_entry, isrange = True):
                write_msg(txt_container, '行、列重复次数填写错误！\n仅支持"n"或者"lxcy"两种形式')
                return

            rules.append((rule_entry, col_entry, row_entry))
        data.append((rect_range, rules))
    # end for

    # combine data
    string = ''
    for rect_data in data:
        for rules in rect_data[1]:
            if len(string) != 0:
                string += '--link '

            string += '%s ' % rules[0]
            # column and row
            string += '-numcolumn=%s ' % rules[1]
            string += '-numline=%s ' % rules[2]
        # end for

        string += '-rectangle={%s} ' % rect_data[0]
    # end for

    print(string)
    if sys.platform == 'win32':
        ret = os.system('generator.exe -exp="%s" 2> error.txt' % string)
    else:
        ret = os.system('./generator -exp="%s" 2> error.txt' % string)

    if ret != 0:
        # get error message
        os.system('sed -i -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})*)?m//g" error.txt')
        write_msg(txt_container, read_file('error.txt'))
    else:
        # show text
        write_msg(txt_container, read_file('input01.txt'))
        os.remove('input01.txt')


# exit function
def exit_func():
    sys.exit(0)

# set separator
ttk.Separator(maingui, orient = "vertical").pack(side = "right", fill = "y", padx = 300, pady = 20)

# # left area
# panes
#left_pw = tk.PanedWindow(maingui, orient = 'vertical', width = 450, height = 420)
left_pw = tk.PanedWindow(maingui, orient = 'vertical', width = 450)
left_pw.place(x = 25, y = 10)
append_func(left_pw)

# # right area
# frame
right_frame = tk.LabelFrame(maingui, text = "生成数据", width = 270, height = 420)
right_frame.place(x = 515, y = 10, anchor = tk.NW)

# set right text container
right_txt = tk.Text(right_frame, state = tk.DISABLED, background = 'LightGrey')
right_txt.place(relwidth = 1, relheight = 1)
vsbar = tk.Scrollbar(right_txt, orient = 'vertical')
vsbar.pack(fill = 'y', side = tk.RIGHT)
vsbar.configure(command = right_txt.yview)
#hsbar = tk.Scrollbar(right_txt, orient = 'horizontal')
#hsbar.pack(fill = 'x', side = tk.BOTTOM)
#hsbar.configure(command = right_txt.xview)
#right_txt.config(xscrollcommand = hsbar.set, yscrollcommand=vsbar.set)
right_txt.config(yscrollcommand=vsbar.set)

# # bottom button
generate_btn = tk.Button(maingui, text = '生成', command = lambda: generate_func(left_pw, right_txt))
append_btn = tk.Button(maingui, text = '增加', command = lambda: append_func(left_pw))
esc_btn = tk.Button(maingui, text = '退出', command = exit_func)

save_btn = tk.Button(maingui, text = '修正', command = lambda: writable_func(right_txt))
change_btn = tk.Button(maingui, text = '保存', command = lambda: save_func(right_txt))

# place
generate_btn.place(x = 95, y = 450, anchor = tk.NW)
append_btn.place(x = 225, y = 450, anchor = tk.NW)
esc_btn.place(x = 355, y = 450, anchor = tk.NW)

save_btn.place(x = 560, y = 450, anchor = tk.NW)
change_btn.place(x = 690, y = 450, anchor = tk.NW)

maingui.mainloop()
