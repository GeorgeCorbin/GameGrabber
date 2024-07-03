from flask import Flask, render_template, request, jsonify
import subprocess
from threading import Thread
from queue import Queue, Empty
import os
import sys

app = Flask(__name__)

LOG_FILE = 'personalLogs'

# Function to handle subprocess output and log to file
def enqueue_output(out, queue):
    with open(LOG_FILE, 'a') as log_file:
        for line in iter(out.readline, ''):
            log_file.write(line)
            log_file.flush()
            queue.put(line)
    out.close()

# Function to run a subprocess and capture output
def run_script(script_name):
    global current_process, stdout_queue, stderr_queue
    try:
        current_process = subprocess.Popen(
            [sys.executable, script_name],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout_queue = Queue()
        stderr_queue = Queue()
        stdout_thread = Thread(target=enqueue_output, args=(current_process.stdout, stdout_queue))
        stderr_thread = Thread(target=enqueue_output, args=(current_process.stderr, stderr_queue))
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()
    except Exception as e:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Error starting script {script_name}: {e}\n")
            log_file.flush()
        print(f"Error starting script {script_name}: {e}")

# Function to get the current output from the process
def get_output():
    output_lines = []
    if current_process:
        while True:
            try:
                line = stdout_queue.get_nowait()
            except Empty:
                break
            else:
                output_lines.append(line.strip())
        while True:
            try:
                line = stderr_queue.get_nowait()
            except Empty:
                break
            else:
                output_lines.append("ERROR: " + line.strip())
    return output_lines

# Global variables to store the script process and its queues
current_process = None
stdout_queue = Queue()
stderr_queue = Queue()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start/<script_name>', methods=['POST'])
def start_script(script_name):
    global current_process
    if current_process is not None and current_process.poll() is None:
        current_process.terminate()
    run_script(script_name)
    return '', 204

@app.route('/submit_input', methods=['POST'])
def submit_input():
    global current_process
    input_value = request.json.get('input')
    if current_process and current_process.poll() is None:
        try:
            current_process.stdin.write(input_value + "\n")
            current_process.stdin.flush()
        except BrokenPipeError:
            with open(LOG_FILE, 'a') as log_file:
                log_file.write("BrokenPipeError: The subprocess has terminated and cannot receive input.\n")
                log_file.flush()
            print("BrokenPipeError: The subprocess has terminated and cannot receive input.")
    return '', 204

@app.route('/get_output', methods=['GET'])
def get_output_route():
    return jsonify(get_output())

# if __name__ == '__main__':
#     app.run(debug=True)
