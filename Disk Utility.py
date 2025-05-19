import os
import ctypes
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, font

fonts = tk.Tk()
fonts.withdraw()  # 隱藏視窗
print(font.families())
fonts.destroy()   # 用完就關掉

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

TEMP_DIR = os.path.dirname(os.path.abspath(__file__))
DISKPART_OUTPUT = os.path.join(TEMP_DIR, "diskpart_output.txt")

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

def showOutput():
    with open(DISKPART_OUTPUT, "r", encoding="utf-8") as f:
        tail = f.read()
    return messagebox.askyesno("執行結果", f"{tail}\n\n是否繼續下一步？")

def listDisk():
    script_path = os.path.join(TEMP_DIR, "list_disk.txt")
    with open(script_path, "w") as f:
        f.write("list disk\n")
    result = subprocess.run(["diskpart", "/s", script_path], capture_output=True, text=True).stdout
    os.remove(script_path)
    return result

def listVolume():
    script_path = os.path.join(TEMP_DIR, "list_volume.txt")
    with open(script_path, "w") as f:
        f.write("list volume\n")
    result = subprocess.run(["diskpart", "/s", script_path], capture_output=True, text=True).stdout
    os.remove(script_path)
    return result

def refreshLists():
    disk_text.delete(1.0, tk.END)
    disk_text.insert(tk.END, listDisk())

    volume_text.delete(1.0, tk.END)
    volume_text.insert(tk.END, listVolume())

def getInput():
    diskNum = disk_entry.get().strip()
    label = label_entry.get().strip()
    letter = letter_entry.get().strip().upper()
    fs_map = {"1": "exfat", "2": "ntfs", "3": "fat32"}
    fs = fs_map.get(fs_var.get(), "exfat")
    quick = "quick" if quick_var.get() == "1" else ""
    gpt = part_var.get() == "2"
    clean_all = clean_var.get() == "2"
    return diskNum, label, letter, fs, quick, gpt, clean_all

def step_clean():
    diskNum, *_ , clean_all = getInput()
    cmd = "clean all" if clean_all else "clean"
    run_diskpart([f"select disk {diskNum}", cmd])
    if showOutput():
        return True
    return False

def step_convert():
    diskNum, *_ , gpt, _ = getInput()
    cmd = "convert gpt" if gpt else "convert mbr"
    run_diskpart([f"select disk {diskNum}", cmd], append=True)
    if showOutput():
        return True
    return False

def createPartition():
    diskNum = disk_entry.get().strip()
    run_diskpart([f"select disk {diskNum}", "create partition primary"], append=True)
    if showOutput():
        return True
    return False

def step_format():
    diskNum, label, _, fs, quick, *_ = getInput()
    if len(label.encode("utf-8")) > 11:
        messagebox.showerror("錯誤", "卷標名稱不能超過 11 個半形字元")
        return False
    run_diskpart([
        f"select disk {diskNum}",
        "select partition 1",
        f"format fs={fs} label=\"{label}\" {quick}"
    ], append=True)
    if showOutput():
        return True
    return False

def assignLetter():
    diskNum, _, letter, *_ = getInput()
    if not letter.isalpha() or len(letter) != 1:
        messagebox.showerror("錯誤", "請輸入磁碟機代號英文字母")
        return False
    run_diskpart([
        f"select disk {diskNum}",
        "select partition 1",
        f"assign letter={letter}"
    ], append=True)
    messagebox.showinfo("完成", f"指定磁碟機代號為 {letter}:\\")
    return True

# GUI 建構
root = tk.Tk()
root.title("Disk Utility")
root.geometry("800x700")

tk.Label(root, text="磁碟清單（Disk）").pack()
disk_text = tk.Text(root, height=10, bg="#1e1e1e", fg="#00ff00")
disk_text.pack(fill="x", padx=10)

tk.Label(root, text="磁區清單（Volume）").pack()
volume_text = tk.Text(root, height=10, bg="#1e1e1e", fg="#00ff00")
volume_text.pack(fill="x", padx=10)

ttk.Button(root, text="重新整理磁碟資訊", command=refreshLists).pack(pady=5)

form_frame = ttk.LabelFrame(root, text="格式化選項")
form_frame.pack(fill="x", padx=10, pady=10)

ttk.Label(form_frame, text="磁碟編號 (e.g. 2)").grid(row=0, column=0)
disk_entry = ttk.Entry(form_frame)
disk_entry.grid(row=0, column=1)

ttk.Label(form_frame, text="清除類型").grid(row=1, column=0)
clean_var = tk.StringVar(value="1")
ttk.Combobox(form_frame, textvariable=clean_var, values=["1", "2"], width=10).grid(row=1, column=1)
ttk.Label(form_frame, text="1=Clean, 2=Clean All").grid(row=1, column=2)

ttk.Label(form_frame, text="分割區類型").grid(row=2, column=0)
part_var = tk.StringVar(value="1")
ttk.Combobox(form_frame, textvariable=part_var, values=["1", "2"], width=10).grid(row=2, column=1)
ttk.Label(form_frame, text="1=MBR, 2=GPT").grid(row=2, column=2)

ttk.Label(form_frame, text="檔案系統").grid(row=3, column=0)
fs_var = tk.StringVar(value="1")
ttk.Combobox(form_frame, textvariable=fs_var, values=["1", "2", "3"], width=10).grid(row=3, column=1)
ttk.Label(form_frame, text="1=exFAT, 2=NTFS, 3=FAT32").grid(row=3, column=2)

ttk.Label(form_frame, text="格式化方式").grid(row=4, column=0)
quick_var = tk.StringVar(value="1")
ttk.Combobox(form_frame, textvariable=quick_var, values=["1", "2"], width=10).grid(row=4, column=1)
ttk.Label(form_frame, text="1=快速格式化, 2=完整格式化").grid(row=4, column=2)

ttk.Label(form_frame, text="卷標名稱 (最多為 11 個字元)").grid(row=5, column=0)
label_entry = ttk.Entry(form_frame)
label_entry.grid(row=5, column=1)

ttk.Label(form_frame, text="磁碟機代號 (如 E)").grid(row=6, column=0)
letter_entry = ttk.Entry(form_frame)
letter_entry.grid(row=6, column=1)

# 按鈕：每步一個按鈕
ttk.Button(root, text="清除磁碟", command=step_clean).pack(pady=2)
ttk.Button(root, text="轉換格式 (MBR/GPT)", command=step_convert).pack(pady=2)
ttk.Button(root, text="建立分割區", command=createPartition).pack(pady=2)
ttk.Button(root, text="格式化", command=step_format).pack(pady=2)
ttk.Button(root, text="指定磁碟機代號", command=assignLetter).pack(pady=2)

refreshLists()
root.mainloop()

