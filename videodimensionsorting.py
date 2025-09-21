import os
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

# ----- ffprobe path (edit if needed) -----
FFPROBE_PATH = r"C:\ffmpeg\bin\ffprobe.exe"  # or r"C:\ffmpeg\bin\ffprobe.exe"

def get_video_resolution(filepath):
    """Return (width, height) of a video using ffprobe."""
    try:
        cmd = [
            FFPROBE_PATH,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=s=x:p=0",
            filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        resolution = result.stdout.strip()
        if resolution:
            width, height = resolution.split("x")
            return int(width), int(height)
    except Exception as e:
        log(f"❌ Could not read resolution for {os.path.basename(filepath)}: {e}")
    return None, None

def sort_videos_by_resolution(source_folder, move_files=True, mode="resolution"):
    if not source_folder:
        messagebox.showwarning("Warning", "Please select a folder first!")
        return

    dest_folder = os.path.join(source_folder, "sorted_videos")
    os.makedirs(dest_folder, exist_ok=True)

    for filename in os.listdir(source_folder):
        if filename.lower().endswith(".mp4"):
            filepath = os.path.join(source_folder, filename)
            width, height = get_video_resolution(filepath)

            if width and height:
                if mode == "resolution":
                    folder_name = f"{width}x{height}"
                elif mode == "type":
                    if width > height:
                        folder_name = "landscape"
                    elif width < height:
                        folder_name = "portrait"
                    else:
                        folder_name = "square"
            else:
                folder_name = "unknown"

            dest_path = os.path.join(dest_folder, folder_name)
            os.makedirs(dest_path, exist_ok=True)

            action = shutil.move if move_files else shutil.copy2
            action(filepath, os.path.join(dest_path, filename))

            log(f"{'Moved' if move_files else 'Copied'} {filename} → {folder_name}")

    log("\n✅ Done! Files sorted into 'sorted_videos'.")

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)
        log(f"📂 Selected folder: {folder}\n")

def start_sorting():
    source_folder = folder_var.get()
    move_files = move_var.get() == 1
    mode = "resolution" if mode_var.get() == 1 else "type"
    sort_videos_by_resolution(source_folder, move_files, mode)

def log(message):
    output.insert(tk.END, message + "\n")
    output.see(tk.END)

# ---------------- GUI ----------------
root = tk.Tk()
root.title("MP4 Sorter")
root.geometry("620x480")

frame = tk.Frame(root)
frame.pack(pady=10)

folder_var = tk.StringVar()
move_var = tk.IntVar(value=1)
mode_var = tk.IntVar(value=1)  # 1 = resolution, 2 = type

tk.Button(frame, text="Select Folder", command=choose_folder).grid(row=0, column=0, padx=5)
tk.Entry(frame, textvariable=folder_var, width=50).grid(row=0, column=1, padx=5)

# Move / Copy options
tk.Label(root, text="File Action:").pack()
tk.Radiobutton(root, text="Move files", variable=move_var, value=1).pack()
tk.Radiobutton(root, text="Copy files", variable=move_var, value=0).pack()

# Sorting mode options
tk.Label(root, text="Sorting Mode:").pack(pady=5)
tk.Radiobutton(root, text="Resolution (e.g., 1920x1080)", variable=mode_var, value=1).pack()
tk.Radiobutton(root, text="Type (Landscape, Square, Portrait)", variable=mode_var, value=2).pack()

tk.Button(root, text="Start Sorting", command=start_sorting, bg="lightblue").pack(pady=10)

output = scrolledtext.ScrolledText(root, width=70, height=15)
output.pack(padx=10, pady=10)

root.mainloop()
