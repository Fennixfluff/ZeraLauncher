#!/usr/bin/env python3

import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageTk
import json
import argparse
import psutil

# Constants and settings
BG_COLOR = "#f5f5dc"
BUTTON_COLOR = "#d3b897"
TEXT_COLOR = "#5b5a5a"
DETAILS_COLOR = "#f8f5e6"
CONFIG_PATH = Path.home() / ".zera_config.json"

DEFAULT_CONFIG = {
    "startup_prevention": True,
    "show_dialog": True
}

running_processes = {}  # path -> psutil.Process

# Helper functions
def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f)

def get_exe_files():
    exe_files = []
    home = os.path.expanduser("~")

    for root, dirs, files in os.walk(home):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 'wine' not in d.lower()]
        for file in files:
            if file.lower().endswith(".exe"):
                exe_files.append(os.path.join(root, file))

    return exe_files

def get_file_details(filepath):
    try:
        stat = os.stat(filepath)
        size = human_readable_size(stat.st_size)
        return f"Path: {filepath}\nSize: {size}"
    except FileNotFoundError:
        return "File not found"

def human_readable_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

# Helper functions
def run_exe(filepath):
    # Ensure old processes are cleaned before running a new one
    clean_running_processes()

    # Start the new process
    proc = subprocess.Popen(["wine", filepath])
    running_processes[str(filepath)] = psutil.Process(proc.pid)

def clean_running_processes():
    """Remove processes from the dictionary that have finished running."""
    for path, proc in list(running_processes.items()):
        try:
            if not proc.is_running():
                # Process has finished, remove from dictionary
                del running_processes[path]
        except psutil.NoSuchProcess:
            # If the process no longer exists, clean it up
            del running_processes[path]

# Modify run_selected to check running processes before running
def run_selected(self):
    selection = self.file_list.curselection()
    if not selection:
        return

    name = self.file_list.get(selection[0]).strip()
    filepath = Path(self.exe_map.get(name)).resolve()

    if self.config_data.get("startup_prevention"):
        clean_running_processes()  # Make sure to clean up old processes first
        proc = running_processes.get(str(filepath))
        if proc and proc.is_running():
            if self.config_data.get("show_dialog"):
                msg = (
                    "Hey there Trainer! We released that pesky 2nd instance for you, cleaning up your pokémon box!\n"
                    "If you want us to stop, run './ZeraLauncher -startup-prevention --disabled'."
                )
                CustomNotification(self, "Zera", msg, "icon2.png")
            return

    run_exe(str(filepath))


# Custom notification class
class CustomNotification(tk.Toplevel):
    def __init__(self, parent, title, message, icon_path):
        super().__init__(parent)
        self.title(title)
        self.geometry("700x120")
        self.config(bg=BG_COLOR)
        self.resizable(False, False)

        # Add icon
        try:
            icon_image = Image.open(icon_path)
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.tk.call('wm', 'iconphoto', self._w, icon_photo)
            self.icon_ref = icon_photo
        except Exception as e:
            print(f"Failed to load icon2.png: {e}")

        # Create content frame
        content_frame = tk.Frame(self, bg=BG_COLOR)
        content_frame.pack(fill="both", expand=True)

        message_label = tk.Label(
            content_frame,
            text=message,
            font=("Arial", 12),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            justify="center",
        )
        message_label.pack(pady=20)

        button = tk.Button(
            content_frame,
            text="OK",
            font=("Arial", 10),
            bg=BUTTON_COLOR,
            fg="white",
            command=self.destroy,
        )
        button.pack(pady=(0, 10))

# Main GUI class
class ZeraLauncher(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.title("ZeraLauncher")
        self.geometry("600x400")
        self.resizable(True, True)
        self.config(bg=BG_COLOR)
        self.selected_file = None
        self.config_data = config

        try:
            icon_image = Image.open("icon.png")
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.tk.call('wm', 'iconphoto', self._w, icon_photo)
            self.icon_ref = icon_photo
        except Exception as e:
            print(f"Failed to load icon.png: {e}")

        self.main_frame = tk.Frame(self, bg=BG_COLOR)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.sidebar_frame = tk.Frame(self, bg=BG_COLOR, width=200)
        self.sidebar_frame.pack(side="right", fill="y")
        self.sidebar_frame.pack_propagate(False)

        self.file_list = tk.Listbox(
            self.main_frame,
            font=("Arial", 12),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.file_list.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        self.file_list.bind("<<ListboxSelect>>", self.on_select)
        self.file_list.bind("<Return>", lambda e: self.run_selected())

        self.scrollbar = tk.Scrollbar(self.file_list, command=self.file_list.yview)
        self.file_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh_button = tk.Button(
            self.file_list,
            text="R",
            font=("Arial", 5),
            command=self.refresh_files,
            relief="flat",
            bg=BUTTON_COLOR,
            fg="white",
            width=1,
            height=1
        )
        self.refresh_button.place(relx=1.0, rely=0.0, anchor="ne", x=-2, y=7)

        self.details_frame = tk.Frame(self.main_frame, bg=DETAILS_COLOR, height=90)
        self.details_frame.pack(fill="x", pady=(0, 5))
        self.details_inner = tk.Frame(self.details_frame, bg=BUTTON_COLOR, bd=2, relief="ridge")
        self.details_inner.pack(fill="both", expand=True, padx=10, pady=10)

        self.details = tk.Label(
            self.details_inner,
            text="Select a file",
            anchor="w",
            justify="left",
            font=("Arial", 14),
            bg=BUTTON_COLOR,
            fg=TEXT_COLOR
        )
        self.details.pack(fill="both", expand=True, padx=10, pady=5)

        self.run_button = tk.Button(
            self.sidebar_frame,
            text="Run",
            command=self.run_selected,
            bg=BUTTON_COLOR,
            fg="white"
        )
        self.run_button.pack(fill="x", padx=5, pady=5)

        try:
            self.icon_bitmap = tk.PhotoImage(file="icon.png")
            self.icon_label = tk.Label(self.sidebar_frame, image=self.icon_bitmap, bg=BG_COLOR)
            self.icon_label.place(relx=0.5, rely=0.96, anchor="s")
        except:
            self.icon_label = None

        self.creator_label = tk.Label(
            self.sidebar_frame,
            text="Made by: The_Shady_Zeraora",
            font=("Arial", 8),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.creator_label.place(relx=0.5, rely=0.98, anchor="s")

        self.refresh_files()

    def refresh_files(self):
        self.file_list.delete(0, tk.END)
        self.exe_map = {}
        for f in get_exe_files():
            filename = os.path.basename(f)
            self.exe_map[filename] = f
            self.file_list.insert(tk.END, filename)

    def on_select(self, event):
        selection = self.file_list.curselection()
        if selection:
            name = self.file_list.get(selection[0]).strip()
            file_path = Path(self.exe_map.get(name)).resolve()
            if file_path.exists():
                details = get_file_details(file_path)
                self.details.config(text=f"Name: {name}\n{details}")

    def run_selected(self):
        selection = self.file_list.curselection()
        if not selection:
            return

        name = self.file_list.get(selection[0]).strip()
        filepath = Path(self.exe_map.get(name)).resolve()

        if self.config_data.get("startup_prevention"):
            proc = running_processes.get(str(filepath))
            if proc and proc.is_running():
                if self.config_data.get("show_dialog"):
                    msg = (
                        "Hey there Trainer! We released that pesky 2nd instance for you, cleaning up your pokémon box!\n"
                        "If you want us to stop, run './ZeraLauncher -startup-prevention --disabled'."
                    )
                    CustomNotification(self, "Zera", msg, "icon2.png")
                return


        run_exe(str(filepath))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-startup-prevention", nargs="?", const="toggle", default=None)
    parser.add_argument("--enabled", action="store_true")
    parser.add_argument("--disabled", action="store_true")
    args = parser.parse_args()

    config = load_config()

    if args.startup_prevention:
        if args.enabled:
            config["startup_prevention"] = True
            save_config(config)
            print("Startup prevention enabled.")
        elif args.disabled:
            config["startup_prevention"] = False
            save_config(config)
            print("Startup prevention disabled.")
        else:
            print("Usage: ./ZeraLauncher -startup-prevention --enabled|--disabled")
        exit()

    app = ZeraLauncher(config)
    app.mainloop()
