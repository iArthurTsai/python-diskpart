import os
import ctypes
import sys
import subprocess
#import re
import tkinter as tk
from tkinter import ttk, messagebox, font

fonts = tk.Tk()
fonts.withdraw()  # 隱藏視窗
print(font.families())
fonts.destroy()   # 用完就關掉

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
if hasattr(sys, '_MEIPASS'):
    icon_path = os.path.join(sys._MEIPASS, 'Disk Utility.ico')
else:
    icon_path = 'Disk Utility.ico'
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
    return messagebox.askyesno("執行結果", f"{tail}\n是否繼續下一步？\n「是」，進行下一步;「否」，重新執行這個步驟")
    refreshLists()

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
            messagebox.showerror("錯誤", f"磁碟編號 {diskNum} 不存在！請重新輸入。")
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
            messagebox.showerror("錯誤", f"磁碟機代號 {letter} 已指派至其他磁碟機！請重新輸入。")
            return None
    except Exception as e:
        messagebox.showerror("錯誤", f"無法驗證磁碟機代號是否存在：\n{e}")
        return None

    clean_cmd = clean_map.get(clean_key)
    convert_cmd = convert_map.get(convert_key)
    fs_cmd = fs_map.get(fs_key)

    return diskNum, label, letter, clean_cmd, convert_cmd, fs_cmd, quick

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
            format_cmd = f'format fs={fs_cmd} quick'
        else:
            format_cmd = f'format fs={fs_cmd}'

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

    success = steps[index]()
    if success:
        root.after(100, lambda: run_step_chain(steps, index + 1))
    else:
        root.after(100, lambda: run_step_chain(steps, index))

# --- GUI 建構 ---
root = tk.Tk()
root.title("Disk Utility")
root.iconbitmap(icon_path)

window_width = root.winfo_screenwidth()    # 取得螢幕寬度
window_height = root.winfo_screenheight()  # 取得螢幕高度

width = 650
height = 750
root.minsize(width, height)    # 設定視窗最小值
left = int((window_width - width)/2)       # 計算左上 x 座標
top = int((window_height - height)/2)      # 計算左上 y 座標
root.geometry(f'{width}x{height}+{left}+{top}')

# 顯示磁碟資訊區域
ttk.Label(root, text="磁碟清單（Disk）").pack()
disk_text = tk.Text(root, height=10, bg="#1e1e1e", fg="#00ff00")
disk_text.pack(fill="x", padx=10)

ttk.Label(root, text="磁區清單（Volume）").pack()
volume_text = tk.Text(root, height=10, bg="#1e1e1e", fg="#00ff00")
volume_text.pack(fill="x", padx=10)

ttk.Button(root, text="重新整理磁碟資訊", command=refreshLists).pack(pady=2)

# 格式化選項區
form_frame = ttk.LabelFrame(root, text="格式化選項")
form_frame.pack(fill="x", padx=10)

# 表單元件
ttk.Label(form_frame, text="磁碟編號 (e.g. 2)").grid(row=0, column=0)
disk_entry = ttk.Entry(form_frame)
disk_entry.grid(row=0, column=1)

ttk.Label(form_frame, text="清除方式").grid(row=1, column=0)
clean_var = tk.StringVar()
ttk.Combobox(form_frame, textvariable=clean_var, values=["", "Clean", "Clean All"], width=10, state="readonly").grid(row=1, column=1)
ttk.Label(form_frame, text="Clean/Clean All").grid(row=1, column=2)

ttk.Label(form_frame, text="磁碟架構").grid(row=2, column=0)
part_var = tk.StringVar()
ttk.Combobox(form_frame, textvariable=part_var, values=["", "MBR", "GPT"], width=10, state="readonly").grid(row=2, column=1)
ttk.Label(form_frame, text="MBR/GPT").grid(row=2, column=2)

ttk.Label(form_frame, text="檔案系統格式").grid(row=3, column=0)
fs_var = tk.StringVar()
ttk.Combobox(form_frame, textvariable=fs_var, values=["", "exFAT", "NTFS", "FAT32"], width=10, state="readonly").grid(row=3, column=1)
ttk.Label(form_frame, text="exFAT/NTFS/FAT32").grid(row=3, column=2)

ttk.Label(form_frame, text="格式化方式").grid(row=4, column=0)
quick_var = tk.BooleanVar()
ttk.Checkbutton(form_frame, text="快速格式化", variable=quick_var).grid(row=4, column=1, sticky="w")

ttk.Label(form_frame, text="卷標名稱 (最多為 11 個字元)").grid(row=5, column=0)
label_entry = ttk.Entry(form_frame)
label_entry.grid(row=5, column=1)

ttk.Label(form_frame, text="磁碟機代號 (如 E)").grid(row=6, column=0)
letter_entry = ttk.Entry(form_frame)
letter_entry.grid(row=6, column=1)

# 操作按鈕:由使用者一個一個按鈕慢慢按
#ttk.Button(root, text="清除磁碟", command=clean).pack(pady=2)
#ttk.Button(root, text="轉換磁碟架構", command=convert).pack(pady=2)
#ttk.Button(root, text="建立磁碟區", command=partition).pack(pady=2)
#ttk.Button(root, text="格式化", command=formatCmd).pack(pady=2)
#ttk.Button(root, text="指派磁碟機代號", command=assignLetter).pack(pady=2)

ttk.Label(root, text="磁碟分割清單（Partition）").pack()
partition_text = tk.Text(root, height=11, bg="#1e1e1e", fg="#00ff00")
partition_text.pack(fill="x", padx=10)

# 自動引導流程按鈕:
ttk.Button(root, text="格式化磁碟", command=lambda: run_step_chain([clean, convert, partition, formatCmd, assignLetter])).pack(pady=2)

refreshLists()
root.mainloop()

# --- 清理臨時檔案 ---
for filename in ["diskpart_script.txt", "list_disk.txt", "list_volume.txt", "list_partition.txt"]:
    path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(path):
        os.remove(path)

if os.path.exists(DISKPART_OUTPUT):
    os.remove(DISKPART_OUTPUT)
