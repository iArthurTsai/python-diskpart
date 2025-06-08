import os
import ctypes
import sys
import subprocess
#import re
import tkinter as tk
from tkinter import ttk, messagebox, font
from tkinter.colorchooser import askcolor

# --- 權限檢查 ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("\n需要以系統管理員權限執行，正在嘗試提權...")
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, __file__, None, 1
    )
    sys.exit()

# --- 初始化 ---
print(tk.TkVersion)

if hasattr(sys, "_MEIPASS"):
    icon_path = os.path.join(sys._MEIPASS, "Disk Utility.ico")
else:
    icon_path = "Disk Utility.ico"
TEMP_DIR = os.path.dirname(os.path.abspath(__file__))
DISKPART_OUTPUT = os.path.join(TEMP_DIR, "diskpart_output.txt")

# --- 對應表 ---
clean_map = {"Clean": "clean", "Clean All": "clean all"}
convert_map = {"MBR": "convert mbr", "GPT": "convert gpt"}
fs_map = {"exFAT": "exfat", "NTFS": "ntfs", "FAT32": "fat32"}

# --- 執行 DiskPart 命令 ---
def run_diskpart(commands, append=False):
    script_path = os.path.join(TEMP_DIR, "diskpart_script.txt")
    with open(script_path, "w") as f:
        for cmd in commands:
            f.write(cmd + "\n")
    result = subprocess.run(["diskpart", "/s", script_path], capture_output=True, text=True)
    mode = "a" if append else "w"
    with open(DISKPART_OUTPUT, mode, encoding="utf-8") as f:
        f.write(result.stdout)
    os.remove(script_path)
    return result.stdout

# --- 顯示輸出結果 ---
def show():
    with open(DISKPART_OUTPUT, "r", encoding="utf-8") as f:
        tail = f.read()[-400:]
    return messagebox.showinfo("分段執行結果", f"{tail}\n繼續下一步？\n請按下一個按鈕或重新執行這個步驟")
    refreshLists()
    
def showOutput():
    with open(DISKPART_OUTPUT, "r", encoding="utf-8") as f:
        tail = f.read()[-400:]
    result = messagebox.askyesnocancel("執行結果", f"{tail}\n是否繼續下一步？\n「是」，進行下一步;「否」，重新執行這個步驟;「取消」，終止流程執行")
    print(result)
    refreshLists()
    return result

# --- 取得磁碟與磁碟區清單 ---
def listDisk():
    script_path = os.path.join(TEMP_DIR, "list_disk.txt")
    with open(script_path, "w") as f:
        f.write("list disk\n")
    result = subprocess.run(["diskpart", "/s", script_path], capture_output=True, text=True).stdout
    os.remove(script_path)

    valid_disks = []
    #for line in result.splitlines():
        #if line.strip().startswith("磁碟"):
            #parts = line.split()
            #if len(parts) > 1 and parts[1].isdigit():
                #valid_disks.append(parts[1])

    parsing = False
    for line in result.splitlines():
        if "###" in line:
            parsing = True  # 從這行之後開始解析
            continue
        if parsing:
            parts = line.strip().split()
            if len(parts) >= 2:
                # 通常磁碟編號在第2欄，可能是 "0"、"1"...
                disk_num = parts[1]
                if disk_num.isdigit():
                    valid_disks.append(disk_num)
                    
    print("可用的磁碟編號：", valid_disks)
    return result, valid_disks  # 回傳原始輸出與可用編號

def listVolume():
    script_path = os.path.join(TEMP_DIR, "list_volume.txt")
    with open(script_path, "w") as f:
        f.write("list volume\n")
    result = subprocess.run(["diskpart", "/s", script_path], capture_output=True, text=True).stdout
    os.remove(script_path)

    valid_volumes = []
    parsing = False
    for line in result.splitlines():
        if "###" in line:
            parsing = True  # 從這行之後開始解析
            continue
        if parsing:
            parts = line.strip().split()
            if len(parts) >= 2:
                # 通常磁碟區編號在第2欄，可能是 "0"、"1"...
                volume_num = parts[1]
                if volume_num.isdigit():
                    valid_volumes.append(volume_num)
                    
    print("可用的磁碟區編號：", valid_volumes)
    return result, valid_volumes  # 回傳原始輸出與可用編號

def listLetter():
    script_path = os.path.join(TEMP_DIR, "list_volume.txt")
    with open(script_path, "w") as f:
        f.write("list volume\n")
    result = subprocess.run(["diskpart", "/s", script_path], capture_output=True, text=True).stdout
    os.remove(script_path)
    
    valid_letters = []
    parsing = False
    #for line in result.splitlines():
        #line = line.strip()
        #if not line:
            #continue
        #if "###" in line:
            #parsing = True
            #continue
        #if parsing:
            #parts = line.split()
            #if len(parts) >= 2:
                #letter_candidate = parts[2]
                #if re.fullmatch(r"[A-Z]", letter_candidate.upper()):
                    #valid_letters.append(letter_candidate.upper())

    for line in result.splitlines():
        if "###" in line:
            parsing = True  # 從這行之後開始解析
            continue
        if parsing:
            parts = line.strip().split()
            if len(parts) >= 2:
                # 通常磁碟機代號在第3欄，可能是 "C"、"D"...
                letter_candidate = parts[2]
                if letter_candidate.isalpha() and len(letter_candidate) == 1:
                    valid_letters.append(letter_candidate.upper())
                    
    print("letter already assigned：", valid_letters)
    return result, valid_letters  # 回傳原始輸出與不可用代號

def listPartition():
    diskNum = disk_entry.get().strip()
    if not diskNum:
        return "請輸入磁碟編號", []
    script_path = os.path.join(TEMP_DIR, "list_partition.txt")
    with open(script_path, "w") as f:
        f.write(f"select disk {diskNum}\n")
        f.write("list partition\n")
    result = subprocess.run(["diskpart", "/s", script_path], capture_output=True, text=True).stdout
    os.remove(script_path)

    valid_partitions = []
    parsing = False
    for line in result.splitlines():
        if "###" in line:
            parsing = True  # 從這行之後開始解析
            continue
        if parsing:
            parts = line.strip().split()
            if len(parts) >= 2:
                # 通常磁碟分割在第2欄，可能是 "1"、"2"...
                partition_num = parts[1]
                if partition_num.isdigit():
                    valid_partitions.append(partition_num)
                    
    print("可用的磁碟分割編號：", valid_partitions)
    return result, valid_partitions  # 回傳原始輸出與可用編號

# --- 更新顯示區域 ---
def refreshLists():
    run_diskpart([f"rescan"])
    disk_output, _ = listDisk()
    disk_text.delete(1.0, tk.END)
    disk_text.insert(tk.END, disk_output)
    volume_output, _ = listVolume()
    volume_text.delete(1.0, tk.END)
    volume_text.insert(tk.END, volume_output)
    _, valid_letters = listLetter()
    partition_output, _ = listPartition()
    partition_text.delete(1.0, tk.END)
    partition_text.insert(tk.END, partition_output)

    if os.path.exists(DISKPART_OUTPUT):
        os.remove(DISKPART_OUTPUT)

# --- 輸入解析 ---
def getInput():
    diskNum = disk_entry.get().strip()
    label = label_entry.get().strip()
    letter = letter_entry.get().strip().upper()
    clean_key = clean_var.get()
    convert_key = part_var.get()
    fs_key = fs_var.get()
    quick = "quick" if quick_var.get() == "1" else ""

    if not diskNum:
        messagebox.showerror("錯誤", "請輸入磁碟編號")
        return None
    elif not diskNum.isdigit():
        messagebox.showerror("錯誤", "磁碟編號為數字")
        return None

    # 確認磁碟編號是否存在
    try:
        _, valid_disks = listDisk()  # 忽略原始輸出，只取磁碟編號清單
        if diskNum not in valid_disks:
            messagebox.showerror("錯誤", f"磁碟編號 {diskNum} 不存在！請重新輸入")
            return None
    except Exception as e:
        messagebox.showerror("錯誤", f"無法驗證磁碟編號是否存在：\n{e}")
        return None

    if not clean_key:
        messagebox.showerror("錯誤", "請選擇清除方式")
        return None

    if not convert_key:
        messagebox.showerror("錯誤", "請選擇磁碟架構")
        return None

    if not fs_key:
        messagebox.showerror("錯誤", "請選擇檔案系統格式")
        return None

    if not letter:
        messagebox.showerror("錯誤", "請輸入磁碟機代號")
        return None
    elif not letter.isalpha() or len(letter) != 1:
        messagebox.showerror("錯誤", "磁碟機代號應為 A~Z 的單一字母")
        return None

    # 確認磁碟機代號是否存在
    try:
        _, valid_letters = listLetter()  # 忽略原始輸出，只取磁碟機代號清單
        if letter in valid_letters:
            messagebox.showerror("錯誤", f"磁碟機代號 {letter} 已指派至其他磁碟機！請重新輸入")
            return None
    except Exception as e:
        messagebox.showerror("錯誤", f"無法驗證磁碟機代號是否存在：\n{e}")
        return None

    clean_cmd = clean_map.get(clean_key)
    convert_cmd = convert_map.get(convert_key)
    fs_cmd = fs_map.get(fs_key)

    return diskNum, label, letter, clean_cmd, convert_cmd, fs_cmd, quick

def diskNumberWrite(*args):
    # 取得使用者輸入
    user_input = Disk.get().strip()
    if not user_input.isdigit():
        diskChecked.set("應為數字")
        refreshLists()
        return
    try:
        _, valid_disks = listDisk()  # 忽略原始輸出，只取磁碟編號清單
        if user_input in valid_disks:
            diskChecked.set(f"{user_input} 可使用")
            refreshLists()
        else:
            diskChecked.set(f"{user_input} 不存在！請重新輸入")
            refreshLists()
    except Exception as e:
        diskChecked.set("檢查失敗")
        refreshLists()

def diskNumberShow(*args):
    print("磁碟編號:", diskChecked.get())

def update_clean_hint(*args):
    key = clean_var.get()
    print("You choose:", key)
    msg = {
        "Clean": "快速清除分割區，但資料容易復原",
        "Clean All": "安全擦除整顆磁碟，花時較久時間",
        "": ""
    }.get(key, "")
    clean_hint.config(text=msg)

def update_part_hint(*args):
    key = part_var.get()
    print("You choose:", key)
    msg = {
        "MBR": "適用於傳統 BIOS、容量小於 2TB",
        "GPT": "支援 UEFI、容量大於 2TB",
        "": ""
    }.get(key, "")
    part_hint.config(text=msg)

def update_fs_hint(*args):
    key = fs_var.get()
    print("You choose:", key)
    msg = {
        "exFAT": "適合跨平台使用（Windows/macOS）",
        "NTFS": "適用於 Windows，macOS 只支援讀取",
        "FAT32": "最廣泛相容，不支援單一檔案超過 4GB",
        "": ""
    }.get(key, "")
    fs_hint.config(text=msg)

def update_quick_hint():
    state = quick_var.get()
    print("Quick format:", state)
    quick_hint.config(text="快速格式化只清除檔案表，不檢查壞軌" if quick_var.get() else "完整格式化會花較長時間，但更安全")

def labelNameWrite(*args):
    # 取得使用者輸入
    user_input = Name.get().strip()
    try:
        encoded = user_input.encode("utf-8")
        if len(encoded) > 11:
            truncated = b""
            for b in encoded:
                if len(truncated) + len(bytes([b])) > 11:
                    break
                truncated += bytes([b])
            decoded = truncated.decode("utf-8", errors="ignore")
            Name11.set(decoded)
        else:
            Name11.set(user_input)
    except Exception as e:
        Name11.set("檢查失敗")

def labelNameShow(*args):
    print("卷標名稱:", Name11.get())

def letterNameWrite(*args):
    # 取得使用者輸入
    user_input = Alphabet.get().strip().upper()
    if not user_input.isalpha() or len(user_input) != 1:
        letterChecked.set("應為 A~Z 的單一字母")
        return
    try:
        _, valid_letters = listLetter()  # 忽略原始輸出，只取磁碟機代號清單
        if user_input in valid_letters:
            letterChecked.set(f"{user_input} 已指派至其他磁碟機！")
        else:
            letterChecked.set(f"{user_input} 可使用")
    except Exception as e:
        letterChecked.set("檢查失敗")

def letterNameShow(*args):
    print("磁碟機代號:", letterChecked.get())

def callback(event):
    print("Left Click at", event.x, event.y)

def mouseMotion(event):
    x = event.x
    y = event.y
    textvar = "Mouse location - x:{}, y:{}".format(x,y)
    var.set(textvar)

def on_exit(event=None):  # event 預設為 None，以兼容按鈕與鍵盤事件
    if messagebox.askokcancel("Exit", "確定要退出嗎？"):
        print("退出")
        for filename in ["diskpart_script.txt", "list_disk.txt", "list_volume.txt", "list_partition.txt"]:
            path = os.path.join(TEMP_DIR, filename)
            if os.path.exists(path):
                os.remove(path)

        if os.path.exists(DISKPART_OUTPUT):
            os.remove(DISKPART_OUTPUT)

        root.destroy()

# --- 各步驟函式 ---
def clean():
    if os.path.exists(DISKPART_OUTPUT):
        os.remove(DISKPART_OUTPUT)
    
    values = getInput()
    if not values:
        return False
    diskNum, label, letter, clean_cmd, convert_cmd, fs_cmd, quick = values
    run_diskpart([f"select disk {diskNum}", clean_cmd])
    return showOutput()

def convert():
    if os.path.exists(DISKPART_OUTPUT):
        os.remove(DISKPART_OUTPUT)
    
    values = getInput()
    if not values:
        return False
    diskNum, label, letter, clean_cmd, convert_cmd, fs_cmd, quick = values
    run_diskpart([f"select disk {diskNum}", convert_cmd], append=True)
    return showOutput()

def partition():
    if os.path.exists(DISKPART_OUTPUT):
        os.remove(DISKPART_OUTPUT)
    
    diskNum = disk_entry.get().strip()
    run_diskpart([f"select disk {diskNum}", "create partition primary"], append=True)
    return showOutput()

def formatCmd():
    if os.path.exists(DISKPART_OUTPUT):
        os.remove(DISKPART_OUTPUT)
    
    values = getInput()
    if not values:
        return False
    diskNum, label, letter, clean_cmd, convert_cmd, fs_cmd, quick = values

    # 處理卷標長度：超過自動截斷
    try:
        encoded = label.encode("utf-8")
        if len(encoded) > 11:
            truncated = b""
            for b in encoded:
                if len(truncated) + len(bytes([b])) > 11:
                    break
                truncated += bytes([b])
            label = truncated.decode("utf-8", errors="ignore")
            messagebox.showwarning("卷標已截斷", f"卷標名稱過長，自動截斷為：{label}")
    except Exception as e:
        messagebox.showwarning("警告", f"處理卷標時出錯，已設為空白。\n錯誤訊息：{e}")
        label = ""

    # 根據是否勾選快速格式化決定是否加上 quick
    if label:
        if quick_var.get():
            format_cmd = f'format fs={fs_cmd} label="{label}" quick'
        else:
            format_cmd = f'format fs={fs_cmd} label="{label}"'
    else:
        if quick_var.get():
            format_cmd = f"format fs={fs_cmd} quick"
        else:
            format_cmd = f"format fs={fs_cmd}"

    # 組合指令
    commands = [f"select disk {diskNum}", "select partition 1", format_cmd]

    # 如果是 MBR，加入 active
    if convert_cmd == "convert mbr":
        commands.append("active")

    run_diskpart(commands, append=True)
    return showOutput()

def assignLetter():
    if os.path.exists(DISKPART_OUTPUT):
        os.remove(DISKPART_OUTPUT)
    
    values = getInput()
    if not values:
        return False
    diskNum, label, letter, clean_cmd, convert_cmd, fs_cmd, quick = values
    run_diskpart([f"select disk {diskNum}", "select partition 1", f"assign letter={letter}"], append=True)
    return showOutput()

def run_step_chain(steps, index=0):
    # 先檢查輸入是否有效
    if index == 0 and not getInput():
        messagebox.showinfo("停止", "請先填寫完欄位。")
        refreshLists()
        return

    if index >= len(steps):
        messagebox.showinfo("完成", "所有步驟皆已完成。")
        refreshLists()
        return

    result = steps[index]()
    
    if result is True:
        # 使用者選「是」→ 下一步
        root.after(100, lambda: run_step_chain(steps, index + 1))
    elif result is False:
        # 使用者選「否」→ 重新執行這一步
        root.after(100, lambda: run_step_chain(steps, index))
    else:
        # 使用者選「取消」→ 終止整個流程
        messagebox.showinfo("已中止", "流程已手動中止。")
        refreshLists()

def change_theme():
    color = askcolor(title="選擇背景顏色")[1]
    if color:
        def is_dark(hex_color):
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            return (r + g + b) / 3 < 128

        dark = is_dark(color)
        bg = color
        fg = "#ffffff" if is_dark(color) else "#000000"

        # 設定背景
        root.configure(bg=bg)
        canvas.configure(bg=bg)

        style = ttk.Style()

        style.configure("TFrame", background=bg, foreground=fg)
        style.configure("TLabelframe", background=bg)
        style.configure("TLabelframe.Label", background=bg, foreground=fg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TEntry", selectbackground=bg, selectforeground=fg)
        style.configure("TCombobox", selectbackground=bg, selectforeground=fg)
        style.configure("TCheckbutton", background=bg, foreground=fg)
        style.configure("TButton", background=bg)
        
        
        '''widget_name = "TFrame"
        print(f"\n💡 {widget_name} 可設的靜態樣式屬性（configure）:")
        print(style.configure(widget_name))
        print(f"\n📐 {widget_name} 的 layout 結構:")
        print(style.layout(widget_name))
        print(f"\n🧩 {widget_name} layout 各元素可改的參數:")
        for element in style.layout(widget_name):
            print(f"  - {element[0]}: {style.element_options(element[0])}")
        print(f"\n🧭 {widget_name} 的互動狀態樣式（map）:")
        print(style.map(widget_name))'''

        # 遍歷所有 widget
        for widget in root.winfo_children():
            apply_theme(widget, bg, fg)

        for widget in scrollable_frame.winfo_children():
            apply_theme(widget, bg, fg)

def apply_theme(widget, bg, fg):
    if isinstance(widget, tk.Text):
        try:
            widget.configure(bg=bg, fg=fg, insertbackground=fg)
        except:
            pass
    for child in widget.winfo_children():
        apply_theme(child, bg, fg)

def change_font_family(family_name):
    # 設定統一的字型與大小
    new_font = font.Font(family=family_name, size=int(size_var.get()))#10)

    #print("\n🖋 原始字型資訊：")

    # 遍歷所有元件
    for widget in root.winfo_children():
        #print_widget_font(widget)
        apply_font(widget, new_font)

    #print("\n🖋 修改後字型資訊：")

    #for widget in root.winfo_children():
        #print_widget_font(widget)

    # 對 ttk 樣式的元件，需額外透過 style 設定
    style = ttk.Style()
    style.configure("TLabel", font=new_font)
    style.configure("TEntry", font=new_font)
    style.configure("TCombobox", font=new_font)
    style.configure("TCheckbutton", font=new_font)
    style.configure("TButton", font=new_font)
    style.configure("TLabelframe.Label", font=new_font)

def print_widget_font(widget):
    try:
        current_font = font.Font(font=widget["font"])
        print(f"{widget.__class__.__name__}: {current_font.actual()}")
    except (tk.TclError, KeyError):
        pass  # 有些 ttk 元件沒有直接 font 屬性

    # 遞迴列印子元件
    for child in widget.winfo_children():
        print_widget_font(child)

def apply_font(widget, new_font):
    try:
        widget.configure(font=new_font)
    except (tk.TclError, KeyError):
        pass  # 某些 widget 不能直接設 font，跳過即可

    # 遞迴處理子元件
    for child in widget.winfo_children():
        apply_font(child, new_font)

# --- GUI 建構 ---
root = tk.Tk()
root.title("Disk Utility")
root.iconbitmap(icon_path)

screen_width = root.winfo_screenwidth()    # 取得螢幕寬度
screen_height = root.winfo_screenheight()  # 取得螢幕高度

width = 700
height = 900
root.resizable(True, True)
root.minsize(width, height)    # 設定視窗最小值
left = int((screen_width - width)/2)       # 計算左上 x 座標
top = int((screen_height - height)/2)      # 計算左上 y 座標
root.geometry(f"{width}x{height}+{left}+{top}")

# 建立 Canvas 和 Scrollbar
canvas = tk.Canvas(root, borderwidth=0)
v_scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
h_scrollbar = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)

# scrollable_frame 是裝進 canvas 的 Frame
scrollable_frame = ttk.Frame(canvas)
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# 把 scrollable_frame 放進 canvas
canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# 🟡 強制 scrollable_frame 的寬度和 canvas 同步，避免多餘空白
def on_canvas_configure(event):
    canvas.itemconfig(canvas_frame, width=event.width)

canvas.bind("<Configure>", on_canvas_configure)

# 滑鼠捲動支援
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def _on_shift_mousewheel(event):
    canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)
#canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * e.delta / 120), "units"))

canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)
#canvas.bind_all("<Shift-MouseWheel>", lambda e: canvas.xview_scroll(int(-1 * e.delta / 120), "units"))

# Scrollbar 綁定 canvas
canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

# 擺放元件：注意 fill + expand 組合
#canvas.pack(side="left", fill="both", expand=True)
#v_scrollbar.pack(side="right", fill="y")
#h_scrollbar.pack(side="bottom", fill="x")
canvas.grid(row=0, column=0, sticky="nsew")
v_scrollbar.grid(row=0, column=1, sticky="ns")
h_scrollbar.grid(row=1, column=0, sticky="ew")

# 讓 grid 區域自動擴展
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# --- 建立字型選單 ---
available_fonts = (font.families())
font_var = tk.StringVar()

# 顯示磁碟資訊區域
ttk.Label(scrollable_frame, text="磁碟清單（Disk）").pack()
disk_text = tk.Text(scrollable_frame, height=10, bg="#000000", fg="#00ff00")
disk_text.pack(fill="x", padx=10)

ttk.Label(scrollable_frame, text="磁區清單（Volume）").pack()
volume_text = tk.Text(scrollable_frame, height=10, bg="#000000", fg="#00ff00")
volume_text.pack(fill="x", padx=10)

ttk.Button(scrollable_frame, text="重新整理磁碟資訊", cursor="exchange", command=refreshLists).pack(pady=2)

# 格式化選項區
form_frame = ttk.LabelFrame(scrollable_frame, text="格式化選項")
form_frame.pack(fill="x", padx=10)

# 設定 column=1 為可擴展欄位（例如 Entry）
form_frame.columnconfigure(1, weight=1)

width=12

# 表單元件
ttk.Label(form_frame, text="磁碟編號", width=width).grid(row=0, column=0, sticky="w")
Disk = tk.StringVar()
#disk_entry = ttk.Entry(form_frame, textvariable=Disk, width=10)
_, valid_disks = listDisk()  # 忽略原始輸出，只取磁碟編號清單
disk_entry = ttk.Combobox(form_frame, textvariable=Disk, values=valid_disks, width=10)
disk_entry.grid(row=0, column=1, sticky="w")

disk_hint = ttk.Label(form_frame, text="輸入上面的磁碟編號（數字）")
disk_hint.grid(row=0, column=2)

diskChecked = tk.StringVar()
disk_entry_checked = ttk.Entry(form_frame, textvariable=diskChecked, state="readonly")
disk_entry_checked.grid(row=0, column=3, sticky="e")

Disk.trace_add("write", diskNumberWrite)
diskChecked.trace_add("write", diskNumberShow)

ttk.Label(form_frame, text="清除方式", width=width).grid(row=1, column=0, sticky="w")
clean_var = tk.StringVar()
ttk.Combobox(form_frame, textvariable=clean_var, values=["", "Clean", "Clean All"], width=10, state="readonly").grid(row=1, column=1, sticky="w")

clean_hint = ttk.Label(form_frame, text="", wraplength=300)
clean_hint.grid(row=1, column=2)

clean_var.trace_add("write", update_clean_hint)
#clean_cb.bind("<<ComboboxSelected>>", update_clean_hint)

ttk.Label(form_frame, text="磁碟架構", width=width).grid(row=2, column=0, sticky="w")
part_var = tk.StringVar()
ttk.Combobox(form_frame, textvariable=part_var, values=["", "MBR", "GPT"], width=10, state="readonly").grid(row=2, column=1, sticky="w")

part_hint = ttk.Label(form_frame, text="", wraplength=300)
part_hint.grid(row=2, column=2)

part_var.trace_add("write", update_part_hint)
#part_cb.bind("<<ComboboxSelected>>", update_part_hint)

ttk.Label(form_frame, text="檔案系統格式", width=width).grid(row=3, column=0, sticky="w")
fs_var = tk.StringVar()
ttk.Combobox(form_frame, textvariable=fs_var, values=["", "exFAT", "NTFS", "FAT32"], width=10, state="readonly").grid(row=3, column=1, sticky="w")

fs_hint = ttk.Label(form_frame, text="", wraplength=300)
fs_hint.grid(row=3, column=2)

fs_var.trace_add("write", update_fs_hint)
#fs_cb.bind("<<ComboboxSelected>>", update_fs_hint)

ttk.Label(form_frame, text="格式化方式", width=width).grid(row=4, column=0, sticky="w")
quick_var = tk.BooleanVar()
ttk.Checkbutton(form_frame, text="快速格式化", variable=quick_var).grid(row=4, column=1, sticky="w")

quick_hint = ttk.Label(form_frame, text="", wraplength=300)
quick_hint.grid(row=4, column=2)

quick_var.trace_add("write", lambda *args: update_quick_hint())

ttk.Label(form_frame, text="卷標名稱", width=width).grid(row=5, column=0, sticky="w")
Name = tk.StringVar()
label_entry = ttk.Entry(form_frame, textvariable=Name)
label_entry.grid(row=5, column=1, sticky="w")

label_hint = ttk.Label(form_frame, text="限制最多11個字元（UTF-8位元組）")
label_hint.grid(row=5, column=2)

#Name11 = tk.StringVar()
#label11 = ttk.Label(form_frame, textvariable = Name11)
#Name11.set("")
#label11.grid(row=5, column=3, sticky="e")

Name11 = tk.StringVar()
label11_entry = ttk.Entry(form_frame, textvariable=Name11, state="readonly")
label11_entry.grid(row=5, column=3, sticky="e")

Name.trace_add("write", labelNameWrite)
Name11.trace_add("write", labelNameShow)

ttk.Label(form_frame, text="磁碟機代號", width=width).grid(row=6, column=0, sticky="w")
Alphabet = tk.StringVar()
letter_entry = ttk.Entry(form_frame, textvariable=Alphabet, width=2)
letter_entry.grid(row=6, column=1, sticky="w")

letter_hint = ttk.Label(form_frame, text="輸入 A~Z 的單一字母，不可與現有重複")
letter_hint.grid(row=6, column=2)

letterChecked = tk.StringVar()
letter_entry_checked = ttk.Entry(form_frame, textvariable=letterChecked, state="readonly")
letter_entry_checked.grid(row=6, column=3, sticky="e")

Alphabet.trace_add("write", letterNameWrite)
letterChecked.trace_add("write", letterNameShow)

# 操作按鈕:由使用者一個一個按鈕慢慢按
#ttk.Button(scrollable_frame, text="清除磁碟", command=clean).pack(pady=2)
#ttk.Button(scrollable_frame, text="轉換磁碟架構", command=convert).pack(pady=2)
#ttk.Button(scrollable_frame, text="建立磁碟區", command=partition).pack(pady=2)
#ttk.Button(scrollable_frame, text="格式化", command=formatCmd).pack(pady=2)
#ttk.Button(scrollable_frame, text="指派磁碟機代號", command=assignLetter).pack(pady=2)

ttk.Label(scrollable_frame, text="磁碟分割清單（Partition）").pack()
partition_text = tk.Text(scrollable_frame, height=11, bg="#000000", fg="#00ff00")
partition_text.pack(fill="x", padx=10)

# 自動引導流程按鈕:
ttk.Button(scrollable_frame, text="格式化磁碟", command=lambda: run_step_chain([clean, convert, partition, formatCmd, assignLetter])).pack(pady=2)

ttk.Button(scrollable_frame, text="選擇主題顏色", cursor="spraycan", command=change_theme).pack(side=tk.RIGHT, padx=10, pady=2)

# ====== 控制字型的 Combobox ======
font_box = ttk.Combobox(scrollable_frame, textvariable=font_var, values=available_fonts, state="readonly", width=32)
font_box.set("新細明體")  # 初始字型
font_box.pack(side=tk.RIGHT, padx=10, pady=2)
font_box.bind("<<ComboboxSelected>>", lambda e: change_font_family(font_var.get()))

# ====== 控制字體大小的 Spinbox ======
size_var = tk.StringVar()#value=str(default_font.cget("size")))
size_var.set("10")
spin = ttk.Spinbox(scrollable_frame, from_=6, to=20, textvariable=size_var, width=3, state="readonly")
spin.pack(side=tk.RIGHT, padx=10, pady=2)

# 若用者手動輸入數字也要更新字型大小
#size_var.trace_add("write", lambda *args: change_font_family(font_var.get()))

root.bind("<Button-1>", callback)

x, y = 0, 0
var = tk.StringVar()
text = "Mouse location - x:{}, y:{}".format(x,y)
var.set(text)
lab = ttk.Label(scrollable_frame, textvariable = var, cursor="mouse")
lab.pack(side=tk.LEFT, padx=10, pady=2)
root.bind("<Motion>", mouseMotion)

# 綁定 Esc 鍵離開
root.bind("<Escape>", on_exit)

# 綁定視窗關閉按鈕（X）離開
root.protocol("WM_DELETE_WINDOW", on_exit)

refreshLists()
root.mainloop()

# --- 清理臨時檔案 ---
for filename in ["diskpart_script.txt", "list_disk.txt", "list_volume.txt", "list_partition.txt"]:
    path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(path):
        os.remove(path)

if os.path.exists(DISKPART_OUTPUT):
    os.remove(DISKPART_OUTPUT)
