import socket
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyautogui
import pygetwindow as gw
import time
import json
import os

# Function to send command to C# overlay
def send_command_to_overlay(command):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 5000))
    client.sendall(command.encode('ascii'))
    client.close()

# Function to check if CS:GO is running
def is_csgo_running():
    windows = gw.getWindowsWithTitle("Counter-Strike 2")
    return len(windows) > 0

# Function to ask for CS:GO path
def ask_for_csgo_path():
    preferences = load_preferences()
    if not is_csgo_running() and preferences['prompt_launch']:
        if messagebox.askyesno("Launch CS:GO", "CS:GO is not running. Do you want to launch it now?"):
            path = filedialog.askopenfilename(title="Select CS:GO Executable", filetypes=[("Executable files", "*.exe")])
            if path:
                with open("csgo_path.txt", "w") as f:
                    f.write(path)
                os.startfile(path)  # Launch the CS:GO executable
                return path
    return None

# Function to save user preferences
def save_preferences(prompt_launch):
    preferences = {'prompt_launch': prompt_launch}
    with open('preferences.json', 'w') as f:
        json.dump(preferences, f)

# Function to load user preferences
def load_preferences():
    if os.path.exists('preferences.json'):
        with open('preferences.json', 'r') as f:
            return json.load(f)
    return {'prompt_launch': True}  # Default value

# Command categories
commands_data = {
    "General": [
        "gotv to fake pov",
        "mirv_listentities isPlayer=1",
        "mirv_pov"
    ],
    "Mirv Streams": [
        "sv_cheats 1",
        "mirv_deathmsg debug 1",
        "mat_postprocess_enable 0",
        "snd_setmixer dialog vol 0",
        "mirv_snd_timescale 1",
        "host_timescale 0",
        "host_framerate 600",
        "mirv_cvar_unhide_all",
        "mat_suppress \"models/props/de_nuke/hr_nuke/nuke_skydome_001/nuke_skydome_001\"",
        "sv_skyname clearsky",
        "mat_suppress \"models/props/de_nuke/hr_nuke/nuke_clouds_001\"",
        "mat_suppress \"models/props/de_nuke/hr_nuke/nuke_clouds_002\"",
        "mat_suppress \"models\\props\\de_cbble\\dist_mountain_a\\dist_mountain_a.mdl\"",
        "exec afx/updateWorkaround",
        "mirv_streams myDepthWorld",
        "mirv_streams mynormal",
        "mirv_streams preview [name]",
        "mirv_streams previewend"
    ],
    "Library & Console": [
        "mirv_loadlibrary \"C:\\nSkinz.dll\"",
        "mirv_listentities isPlayer=1",
        "mat_postprocess_enable 0"
    ],
    "Camera Path": [
        "mirv_input camera",
        "mirv_fov 40",
        "r_drawviewmodel 0",
        "demo_gototick",
        "bind mouse3 \"mirv_campath add; echo campath added\"",
        "bind b \"mirv_time mode resumePaused\"",
        "bind n \"demo_togglepause\"",
        "mirv_campath draw enabled 1",
        "mirv_campath clear",
        "mirv_campath enabled 1"
    ],
    "Reshade": [
        "alias vguiOff \"r_drawvgui 0; alias vgui vguiOn\"",
        "alias vguiOn \"r_drawvgui 1; alias vgui vguiOff\"",
        "alias vgui vguiOff",
        "bind \"f8\" vgui"
    ],
    "Faking Clips": [
        "sv_cheats 1",
        "mp_autoteambalance 0",
        "mp_limitteams 0",
        "mp_restartgame 1",
        "mp_roundtime 60",
        "mp_startmoney 65535",
        "record demoname"
    ],
    "Demo": [
        "bind \"RSHIFT\" demo_togglepause",
        "bind \"RCTRL\" demoui"
    ]
}

def focus_cs2_window(window_title="Counter-Strike 2"):
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        windows[0].activate()
        time.sleep(1)

def execute_commands(commands):
    try:
        if not is_csgo_running():
            path = ask_for_csgo_path()
            if not path:
                return
        focus_cs2_window()
        for i, command in enumerate(commands):
            pyautogui.typewrite(command)
            pyautogui.press('enter')
            time.sleep(0.1)
            progress_var.set((i + 1) / len(commands) * 100)
            root.update_idletasks()
        status_label.config(text="Commands executed.")
    except Exception as e:
        status_label.config(text=f"Error: {e}")

def execute_selected_commands(command_listbox):
    selected_commands = [command_listbox.get(i) for i in command_listbox.curselection()]
    status_label.config(text="Starting command execution...")
    progress_var.set(0)
    root.update_idletasks()
    time.sleep(5)
    execute_commands(selected_commands)
    send_command_to_overlay("update_overlay")

def open_command_editor(command_listbox, selected_command_index):
    editor_window = tk.Toplevel(root)
    editor_window.title("Command Editor")
    tk.Label(editor_window, text="Edit Command:", font=("Arial", 12)).pack(pady=5)
    command_entry = tk.Entry(editor_window, font=("Arial", 12), width=50)
    command_entry.pack(pady=5)
    command_entry.insert(0, command_listbox.get(selected_command_index))

    def save_command():
        new_command = command_entry.get()
        command_listbox.delete(selected_command_index)
        command_listbox.insert(selected_command_index, new_command)
        editor_window.destroy()

    tk.Button(editor_window, text="Save Command", command=save_command, font=("Arial", 12)).pack(pady=20)

def save_command_set(command_listbox, tab_name):
    commands = list(command_listbox.get(0, tk.END))
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'w') as f:
            json.dump({"tab_name": tab_name, "commands": commands}, f)
        status_label.config(text=f"Commands saved to {file_path}")

def load_command_set(command_listbox):
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'r') as f:
            data = json.load(f)
            commands = data["commands"]
            command_listbox.delete(0, tk.END)
            for command in commands:
                command_listbox.insert(tk.END, command)
        status_label.config(text=f"Commands loaded from {file_path}")

# Function to execute batch commands from a file
def execute_batch_commands():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'r') as file:
            commands = [line.strip() for line in file if line.strip()]
            status_label.config(text="Starting batch execution...")
            progress_var.set(0)
            root.update_idletasks()
            time.sleep(5)
            execute_commands(commands)

def show_main_window():
    global root, status_label, progress_var

    root = tk.Tk()
    root.title("CS2 Command Executor")
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=1, fill="both", padx=10, pady=10)

    for tab_name, commands in commands_data.items():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=tab_name)

        command_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, height=15, font=("Arial", 12))
        command_listbox.pack(padx=10, pady=10, expand=True, fill='both')
        for command in commands:
            command_listbox.insert(tk.END, command)

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10, fill='x')

        ttk.Button(button_frame, text="Execute Selected", command=lambda cl=command_listbox: execute_selected_commands(cl)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Selected Command", command=lambda cl=command_listbox: open_command_editor(cl, command_listbox.curselection()[0])).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Save Commands", command=lambda cl=command_listbox, tn=tab_name: save_command_set(cl, tn)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Load Commands", command=lambda cl=command_listbox: load_command_set(cl)).pack(side='left', padx=5)

    ttk.Button(root, text="Execute Batch Commands", command=execute_batch_commands, style="TButton").pack(pady=20)

    status_label = ttk.Label(root, text="", font=("Arial", 12))
    status_label.pack(pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(pady=10, fill=tk.X)

    root.mainloop()

show_main_window()
