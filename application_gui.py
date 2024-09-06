import os
import sys
import tkinter as tk
import subprocess
from threading import Thread
from queue import Queue, Empty


def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')


def configure_widget(widget, **kwargs):
    widget.configure(**kwargs)


def configure_widgets(widgets, **kwargs):
    for widget in widgets:
        widget.configure(**kwargs)


def toggle_dark_mode():
    mode = 'dark' if dark_mode.get() else 'light'
    colors = {
        'dark': {'bg': 'gray20', 'fg': 'white', 'entry_bg': 'gray40', 'entry_fg': 'white', 'button_bg': 'white',
                 'button_fg': 'black', 'button_active_bg': 'lightgray'},
        'light': {'bg': 'white', 'fg': 'black', 'entry_bg': 'white', 'entry_fg': 'black', 'button_bg': 'white',
                  'button_fg': 'black', 'button_active_bg': 'lightgray'}
    }

    root_bg = colors[mode]['bg']
    fg_color = colors[mode]['fg']
    entry_bg = colors[mode]['entry_bg']
    entry_fg = colors[mode]['entry_fg']
    button_bg = colors[mode]['button_bg']
    button_fg = colors[mode]['button_fg']
    button_active_bg = colors[mode]['button_active_bg']

    configure_widget(root, bg=root_bg)
    configure_widgets([input_label, toggle_label], bg=root_bg, fg=fg_color)
    configure_widgets([input_entry], bg=entry_bg, fg=entry_fg)
    configure_widgets([button1, button2, input_submit], bg=button_bg, fg=button_fg, activebackground=button_active_bg)
    configure_widgets([toggle_frame, console_output_frame], bg=root_bg)
    input_frame.config(bg=root_bg)
    toggle_button.itemconfig(toggle_button_text, fill=fg_color)
    toggle_button.itemconfig(toggle_button_circle, fill=fg_color)

    if mode == 'dark':
        toggle_button.coords(toggle_button_circle, 40, 5, 70, 35)
    else:
        toggle_button.coords(toggle_button_circle, 5, 5, 35, 35)


def enqueue_output(out, queue):
    for line in iter(out.readline, ''):
        queue.put(line)
    out.close()


def update_output():
    try:
        while True:
            line = output_queue.get_nowait()
            if "Enter" in line:
                input_prompt = line.strip()
                console_output.insert(tk.END, f"\n{input_prompt}\n")
                input_entry.config(state=tk.NORMAL)
                input_submit.config(state=tk.NORMAL)
                break
            else:
                console_output.insert(tk.END, line)
                console_output.see(tk.END)
    except Empty:
        pass
    root.after(100, update_output)


def run_script(script_name, input_text=None):
    global first_run, process
    if not first_run:
        console_output.insert(tk.END, "\n\nNew Run\n\n")
    else:
        first_run = False

    console_output.see(tk.END)

    # Determine the path to the script
    if getattr(sys, 'frozen', False):
        # If running as a packaged executable
        script_path = os.path.join(sys._MEIPASS, script_name)
    else:
        # If running in a normal Python environment
        script_path = os.path.join(os.path.dirname(__file__), script_name)

    cmd = ["python3", script_path]
    if input_text:
        cmd.append(input_text)

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
    Thread(target=enqueue_output, args=(process.stdout, output_queue), daemon=True).start()
    Thread(target=enqueue_output, args=(process.stderr, output_queue), daemon=True).start()
    update_output()


def run_ESPN():
    run_script("espn_data_retriever.py")


def run_script2():
    run_script("general_scrapper.py")


def on_input_submit():
    input_text = input_entry.get()
    console_output.insert(tk.END, f"{input_text}\n")
    console_output.see(tk.END)
    process.stdin.write(input_text + "\n")
    process.stdin.flush()
    input_entry.delete(0, tk.END)
    input_entry.config(state=tk.DISABLED)
    input_submit.config(state=tk.DISABLED)
    update_output()


# Create the main window
root = tk.Tk()
root.title("Game Snatcher")
center_window(root, 800, 600)

# Create widgets
button1 = tk.Button(root, text="ESPN Game Grabber", font=("Arial", 14), command=run_ESPN)
button2 = tk.Button(root, text="General Scrapper", font=("Arial", 14), command=run_script2)

input_frame = tk.Frame(root, bd=1, relief="solid")
input_label = tk.Label(input_frame, text="Script Input:", font=("Arial", 12))
input_entry = tk.Entry(input_frame, font=("Arial", 12), state=tk.DISABLED)
input_submit = tk.Button(input_frame, text="Submit Input", font=("Arial", 12), command=on_input_submit,
                         state=tk.DISABLED)

console_output_frame = tk.Frame(root, bd=1, relief="solid")
console_output = tk.Text(console_output_frame, wrap='word', height=20, width=100, bg='white', fg='black', bd=0)
scrollbar = tk.Scrollbar(console_output_frame, command=console_output.yview)
console_output.config(yscrollcommand=scrollbar.set)

dark_mode = tk.BooleanVar()
toggle_frame = tk.Frame(root, bg='white')
toggle_label = tk.Label(toggle_frame, text="Color Theme", font=("Arial", 10), bd=1, relief="solid", bg='white')
toggle_button = tk.Canvas(toggle_frame, width=75, height=40, bg='white', highlightthickness=0)
toggle_button.create_rectangle(0, 0, 75, 40, fill="gray70", outline="black", width=2)
toggle_button_text = toggle_button.create_text(37.5, 20, text="", fill="black", font=("Arial", 10))
toggle_button_circle = toggle_button.create_oval(5, 5, 35, 35, fill="black", outline="black")

# Pack and place widgets
button1.pack(pady=10)
# button2.pack(pady=10)

console_output_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
console_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

input_frame.pack(pady=10, padx=10, fill=tk.X)
input_label.grid(row=0, column=0, padx=5, pady=5)
input_entry.grid(row=0, column=1, padx=5, pady=5)
input_submit.grid(row=1, columnspan=2, pady=10)

toggle_frame.place(x=710, y=10)
toggle_label.pack()
toggle_button.pack()

toggle_button.bind("<Button-1>", lambda event: dark_mode.set(not dark_mode.get()) or toggle_dark_mode())


def on_button_press(event):
    event.widget.config(bg=event.widget.cget('activebackground'))


def on_button_release(event):
    event.widget.config(bg=event.widget.cget('bg'))


# Bind button press and release events for click effect
for btn in [button1, button2, input_submit]:
    btn.bind("<ButtonPress-1>", on_button_press)
    btn.bind("<ButtonRelease-1>", on_button_release)

# Initialize output queue, first_run flag, process variable, and start the application
output_queue = Queue()
first_run = True
process = None
root.mainloop()
