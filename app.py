from flask import Flask, render_template, request, redirect, url_for
import subprocess
from threading import Thread
from queue import Queue, Empty
import os
import sys

app = Flask(__name__)

# Function to handle subprocess output
def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

# Function to run a subprocess and capture output
def run_script(script_name, input_value):
    process = subprocess.Popen(
        [sys.executable, script_name],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout_queue = Queue()
    stdout_thread = Thread(target=enqueue_output, args=(process.stdout, stdout_queue))
    stdout_thread.daemon = True
    stdout_thread.start()
    
    if input_value:
        process.stdin.write(input_value + "\n")
        process.stdin.flush()
    
    output_lines = []
    while True:
        try:
            line = stdout_queue.get_nowait()
        except Empty:
            if process.poll() is not None:
                break
        else:
            output_lines.append(line)
    
    return output_lines

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle script execution
@app.route('/run_script', methods=['POST'])
def run_script_route():
    script_name = request.form['script']
    input_value = request.form['input']
    output = run_script(script_name, input_value)
    return render_template('index.html', output=output)

if __name__ == '__main__':
    app.run(debug=True)

