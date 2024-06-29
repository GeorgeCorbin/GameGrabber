import tkinter as tk
from tkinter import messagebox
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
        'dark': {'bg': 'gray20', 'fg': 'white', 'entry_bg': 'gray40', 'entry_fg': 'white'},
        'light': {'bg': 'white', 'fg': 'black', 'entry_bg': 'white', 'entry_fg': 'black'}
    }

    root_bg = colors[mode]['bg']
    fg_color = colors[mode]['fg']
    entry_bg = colors[mode]['entry_bg']
    entry_fg = colors[mode]['entry_fg']

    configure_widget(root, bg=root_bg)
    configure_widgets([label, input_label, input_submit, toggle_label], bg=root_bg, fg=fg_color)
    configure_widgets([entry, input_entry], bg=entry_bg, fg=entry_fg)
    configure_widgets([toggle_frame, console_output_frame], bg=root_bg)
    toggle_button.itemconfig(toggle_button_text, fill=fg_color)
    toggle_button.itemconfig(toggle_button_circle, fill=fg_color)

    if mode == 'dark':
        toggle_button.coords(toggle_button_circle, 40, 5, 70, 35)
    else:
        toggle_button.coords(toggle_button_circle, 5, 5, 35, 35)


def on_button_click():
    entered_text = entry.get()
    if entered_text:
        label.config(text=f"Hello, {entered_text}!")
    else:
        messagebox.showwarning("Input Error", "Please enter some text")


def enqueue_output(out, queue):
    for line in iter(out.readline, ''):
        queue.put(line)
    out.close()


def update_output():
    try:
        while True:
            line = output_queue.get_nowait()
            console_output.insert(tk.END, line)
            console_output.see(tk.END)
    except Empty:
        pass
    root.after(100, update_output)


def run_script(script_name, input_text=None):
    console_output.insert(tk.END, "\n\nNew Run\n\n")
    console_output.see(tk.END)

    cmd = ["python", script_name]
    if input_text:
        cmd.append(input_text)

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    Thread(target=enqueue_output, args=(process.stdout, output_queue), daemon=True).start()
    Thread(target=enqueue_output, args=(process.stderr, output_queue), daemon=True).start()
    update_output()


def run_ESPN():
    run_script("espnScrapper.py")


def run_script2():
    run_script("script2.py")


def on_input_submit():
    input_text = input_entry.get()
    run_script("espnScrapper.py", input_text)


# Create the main window
root = tk.Tk()
root.title("Game Snatcher")
center_window(root, 800, 600)

# Create widgets
label = tk.Label(root, text="Enter your name:", font=("Arial", 14))
entry = tk.Entry(root, font=("Arial", 14))
button = tk.Button(root, text="Submit", font=("Arial", 14), command=on_button_click)
button1 = tk.Button(root, text="ESPN Game Grabber", font=("Arial", 14), command=run_ESPN)
button2 = tk.Button(root, text="Run Script 2", font=("Arial", 14), command=run_script2)

input_frame = tk.Frame(root, bd=1, relief="solid")
input_label = tk.Label(input_frame, text="Script Input:", font=("Arial", 12))
input_entry = tk.Entry(input_frame, font=("Arial", 12))
input_submit = tk.Button(input_frame, text="Submit Input", font=("Arial", 12), command=on_input_submit)

console_output_frame = tk.Frame(root, bd=1, relief="solid")
console_output = tk.Text(console_output_frame, wrap='word', height=10, width=100, bg='white', fg='black', bd=0)
scrollbar = tk.Scrollbar(console_output_frame, command=console_output.yview)

dark_mode = tk.BooleanVar()
toggle_frame = tk.Frame(root, bg='white')
toggle_label = tk.Label(toggle_frame, text="Color Theme", font=("Arial", 10), bd=1, relief="solid", bg='white')
toggle_button = tk.Canvas(toggle_frame, width=75, height=40, bg='white', highlightthickness=0)
toggle_button.create_rectangle(0, 0, 75, 40, fill="gray70", outline="black", width=2)
toggle_button_text = toggle_button.create_text(37.5, 20, text="", fill="black", font=("Arial", 10))
toggle_button_circle = toggle_button.create_oval(5, 5, 35, 35, fill="black", outline="black")

# Pack and place widgets
label.pack(pady=10)
entry.pack(pady=10)
button.pack(pady=10)
button1.pack(pady=10)
button2.pack(pady=10)

input_frame.pack(pady=10, padx=10, fill=tk.X)
input_label.grid(row=0, column=0, padx=5, pady=5)
input_entry.grid(row=0, column=1, padx=5, pady=5)
input_submit.grid(row=1, columnspan=2, pady=10)

console_output_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
console_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
console_output.config(yscrollcommand=scrollbar.set)

toggle_frame.place(x=710, y=10)
toggle_label.pack()
toggle_button.pack()

toggle_button.bind("<Button-1>", lambda event: dark_mode.set(not dark_mode.get()) or toggle_dark_mode())

# Initialize output queue and start the application
output_queue = Queue()
root.mainloop()
