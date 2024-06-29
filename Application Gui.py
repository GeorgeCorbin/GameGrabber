import tkinter as tk
from tkinter import messagebox
import subprocess
from threading import Thread
from queue import Queue, Empty


def center_window(root, width, height):
    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate position x and y coordinates
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root.geometry(f'{width}x{height}+{x}+{y}')


def toggle_dark_mode():
    if dark_mode.get():
        root.configure(bg='gray20')
        label.configure(bg='gray20', fg='white')
        entry.configure(bg='gray40', fg='white')
        toggle_frame.configure(bg='gray20')
        toggle_label.configure(bg='gray20', fg='white')
        toggle_button.itemconfig(toggle_button_text, fill='white')
        toggle_button.itemconfig(toggle_button_circle, fill='white')
        toggle_button.coords(toggle_button_circle, 40, 5, 70, 35)
    else:
        root.configure(bg='white')
        label.configure(bg='white', fg='black')
        entry.configure(bg='white', fg='black')
        toggle_frame.configure(bg='white')
        toggle_label.configure(bg='white', fg='black')
        toggle_button.itemconfig(toggle_button_text, fill='black')
        toggle_button.itemconfig(toggle_button_circle, fill='black')
        toggle_button.coords(toggle_button_circle, 5, 5, 35, 35)

def on_button_click():
    entered_text = entry.get()
    if (entered_text):
        label.config(text=f"Hello, {entered_text}!")
    else:
        messagebox.showwarning("Input Error", "Please enter some text")

def run_script(script_name):
    process = subprocess.Popen(["python", script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    q = Queue()

    def enqueue_output(out, queue):
        for line in iter(out.readline, ''):
            queue.put(line)
        out.close()

    Thread(target=enqueue_output, args=(process.stdout, q), daemon=True).start()
    Thread(target=enqueue_output, args=(process.stderr, q), daemon=True).start()

    def update_output():
        try:
            while True:
                line = q.get_nowait()
                console_output.insert(tk.END, line)
                console_output.see(tk.END)
        except Empty:
            pass
        root.after(100, update_output)

    update_output()

# Running other processes
def run_ESPN():
    run_script("espnScrapper.py")

def run_script2():
    subprocess.run(["python", "script2.py"])

# Create the main window
root = tk.Tk()
root.title("Game Snatcher")

# Set the size and position of the window
window_width = 800
window_height = 500
center_window(root, window_width, window_height)

# Create a label
label = tk.Label(root, text="Enter your name:", font=("Arial", 14))
label.pack(pady=10)

# Create an entry field
entry = tk.Entry(root, font=("Arial", 14))
entry.pack(pady=10)

# Create a button
button = tk.Button(root, text="Submit", font=("Arial", 14), command=on_button_click)
button.pack(pady=10)

# Create new buttons to run other Python scripts
button1 = tk.Button(root, text="ESPN Game Grabber", font=("Arial", 14), command=run_ESPN())
button1.pack(pady=10)

button2 = tk.Button(root, text="Run Script 2", font=("Arial", 14), command=run_script2)
button2.pack(pady=10)

# Create a text widget to display console output
console_output = tk.Text(root, wrap='word', height=10, width=100)
console_output.pack(pady=10)

# Create a toggle switch for dark mode
dark_mode = tk.BooleanVar()

# Create a Frame widget for the toggle switch
toggle_frame = tk.Frame(root)
toggle_frame.place(x=710, y=10)  # Precise positioning (near top-right corner)

toggle_label = tk.Label(toggle_frame, text="Color Theme", font=("Arial", 10), bd=1, relief="solid", bg="white")
toggle_label.pack()

toggle_button = tk.Canvas(toggle_frame, width=75, height=40, bg='white', highlightthickness=0)
toggle_button.pack()

# Create the switch background
toggle_button.create_rectangle(0, 0, 75, 40, fill="gray70", outline="black", width=2)
toggle_button_text = toggle_button.create_text(37.5, 20, text="", fill="black", font=("Arial", 10))

# Create the switch circle
toggle_button_circle = toggle_button.create_oval(5, 5, 35, 35, fill="black", outline="black")

def on_toggle(event):
    dark_mode.set(not dark_mode.get())
    toggle_dark_mode()

toggle_button.bind("<Button-1>", on_toggle)


# Run the application
root.mainloop()
