import os
import shutil
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

DESKTOP_PATH = str(Path.home() / "Desktop")
UNDO_RECORD = os.path.join(DESKTOP_PATH, ".organize_undo.json")

FILE_CATEGORIES = {
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "文档": [".doc", ".docx", ".pdf", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "视频": [".mp4", ".avi", ".mov", ".wmv", ".flv"],
    "音乐": [".mp3", ".wav", ".aac", ".flac"],
    "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "程序": [".exe", ".msi", ".bat", ".py", ".sh"],
    "其他": []
}

def organize_files(selected_types):
    moved_files = []
    for item in os.listdir(DESKTOP_PATH):
        src = os.path.join(DESKTOP_PATH, item)
        if os.path.isfile(src) and not item.startswith(".organize_undo"):
            ext = os.path.splitext(item)[1].lower()
            if ext in selected_types:
                folder_name = ext[1:].upper()
                dst_dir = os.path.join(DESKTOP_PATH, folder_name)
                os.makedirs(dst_dir, exist_ok=True)
                dst = os.path.join(dst_dir, item)
                shutil.move(src, dst)
                moved_files.append({"from": src, "to": dst, "folder": folder_name})
    if moved_files:
        with open(UNDO_RECORD, "w", encoding="utf-8") as f:
            json.dump(moved_files, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("提示", "归类完成。")
    else:
        messagebox.showinfo("提示", "没有需要归类的文件。")

def undo_organize():
    if not os.path.exists(UNDO_RECORD):
        messagebox.showinfo("提示", "没有可撤回的操作。")
        return
    with open(UNDO_RECORD, "r", encoding="utf-8") as f:
        moved_files = json.load(f)
    for record in moved_files:
        if os.path.exists(record["to"]):
            shutil.move(record["to"], record["from"])
    folders = set(r["folder"] for r in moved_files)
    for folder in folders:
        folder_path = os.path.join(DESKTOP_PATH, folder)
        if os.path.isdir(folder_path) and not os.listdir(folder_path):
            try:
                os.rmdir(folder_path)
            except Exception:
                pass
    os.remove(UNDO_RECORD)
    messagebox.showinfo("提示", "撤回成功。")

def show_subtype_window(category):
    subtypes = FILE_CATEGORIES[category]
    if not subtypes:
        messagebox.showinfo("提示", f"{category} 没有可选的文件类型。")
        return

    sub_win = tk.Toplevel()
    sub_win.title(f"选择{category}类型")
    sub_win.geometry("250x400")
    tk.Label(sub_win, text=f"请选择要归类的{category}类型：").pack(anchor="w", padx=10, pady=10)

    var_dict = {}
    for ext in subtypes:
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(sub_win, text=ext, variable=var)
        cb.pack(anchor="w", padx=20)
        var_dict[ext] = var

    def on_organize():
        selected = [ext for ext, var in var_dict.items() if var.get()]
        if not selected:
            messagebox.showwarning("警告", "请至少选择一个文件类型。")
            return
        organize_files(selected)
        sub_win.destroy()

    tk.Button(sub_win, text="归类", command=on_organize, width=10).pack(pady=15)

def start_gui():
    root = tk.Tk()
    root.title("桌面文件类型归类器")
    root.geometry("320x500")

    tk.Label(root, text="请选择要归类的大类：").pack(anchor="w", padx=10, pady=10)

    for cat in FILE_CATEGORIES.keys():
        btn = tk.Button(root, text=cat, width=15, command=lambda c=cat: show_subtype_window(c))
        btn.pack(anchor="w", padx=30, pady=5)

    def on_undo():
        undo_organize()

    tk.Button(root, text="撤回", command=on_undo, width=10).pack(pady=30)

    root.mainloop()

if __name__ == "__main__":
    start_gui()