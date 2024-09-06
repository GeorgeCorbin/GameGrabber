import os
import requests
import pandas as pd
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from queue import Queue, Empty
import time

app = Flask(__name__)

def fetch_all_sports():
    url = "https://sports.core.api.espn.com/v2/sports?limit=1000"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_leagues_for_sport(sports_id):
    url = f"http://sports.core.api.espn.com/v2/sports/{sports_id}/leagues?limit=1000"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_scoreboard_data(sport, league, start_date, end_date):
    url = f"http://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard?limit=1000&dates={start_date}-{end_date}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def parse_scoreboard(json_data, sport, league):
    games = []
    for event in json_data.get('events', []):
        game_data = {}
        if sport == "mma" and league == "ufc":
            game_data['Event'] = event.get('name', 'N/A')
            game_data['Date'] = event.get('date', 'N/A')
            competitions = event.get('competitions', [])
            for comp_index, competition in enumerate(competitions):
                comp_key = f"Competition_{comp_index+1}"
                competitors = competition.get('competitors', [])
                for comp_index, competitor in enumerate(competitors):
                    comp_prefix = f"{comp_key}_Competitor_{comp_index+1}"
                    game_data[f"{comp_prefix}_Athlete_FullName"] = competitor.get('athlete', {}).get('displayName', 'N/A')
                    game_data[f"{comp_prefix}_Winner"] = competitor.get('winner', 'N/A')
        else:
            competitions = event.get('competitions', [])
            if competitions:
                competitors = competitions[0].get('competitors', [])
                if competitors:
                    game_data['Away Team'] = competitors[0].get('team', {}).get('displayName', 'N/A')
                    game_data['Away Score'] = competitors[0].get('score', 'N/A')
                    game_data['Home Team'] = competitors[1].get('team', {}).get('displayName', 'N/A')
                    game_data['Home Score'] = competitors[1].get('score', 'N/A')
            status = event.get('status', {}).get('type', {}).get('description', 'N/A')
            game_data['Status'] = status
        games.append(game_data)
    return games

def save_scoreboard_to_csv(games, filename):
    df = pd.DataFrame(games)
    downloads_dir = os.path.join(app.root_path, 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    file_path = os.path.join(downloads_dir, filename)
    df.to_csv(file_path, index=False)
    print(f"Scoreboard data saved to {filename}")
    return filename

def extract_sport_id(sport_url):
    match = re.search(r"sports/([^?]+)", sport_url)
    return match.group(1) if match else None

def extract_league_id(league_url):
    match = re.search(r"leagues/([^?]+)", league_url)
    return match.group(1) if match else None

def display_sports_options(sports):
    sports_list = []
    for sport in sports:
        sport_id = extract_sport_id(sport['$ref'])
        if sport_id:
            sports_list.append(sport_id)
    return sports_list

def display_league_options(leagues):
    leagues_list = []
    for league in leagues:
        league_id = extract_league_id(league['$ref'])
        if league_id:
            leagues_list.append(league_id)
    return leagues_list

def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

def parse_events_data(events):
    parsed_data = []
    for event in events:
        flattened_event = flatten_json(event)
        parsed_data.append(flattened_event)
    return parsed_data

def export_to_csv(parsed_data, filename):
    df = pd.DataFrame(parsed_data)
    downloads_dir = os.path.join(app.root_path, 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    file_path = os.path.join(downloads_dir, filename)
    df.to_csv(file_path, index=False)
    print(f"Extra Data exported to {filename}")
    return filename

def enqueue_output(out, queue):
    for line in iter(out.readline, ''):
        queue.put(line)
    out.close()

def run_scraper(sport_id, league_id, start_date, end_date):
    try:
        json_data = fetch_scoreboard_data(sport_id, league_id, start_date, end_date)
        games = parse_scoreboard(json_data, sport_id, league_id)
        if games:
            filename = f"{sport_id}_{league_id}_scoreboard.csv"
            file_path = save_scoreboard_to_csv(games, filename)
        else:
            print("No scoreboard data found.")
            return None

        data = fetch_scoreboard_data(sport_id, league_id, start_date, end_date)
        events = data.get('events', [])
        parsed_data = parse_events_data(events)
        extra_file_path = export_to_csv(parsed_data, f'Extra_{sport_id}_{league_id}_events_data.csv')

        return file_path, extra_file_path
    except requests.RequestException as e:
        print(f"Failed to fetch data from ESPN API. Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_output():
    output_lines = []
    if current_process:
        time.sleep(5)  # Add a delay to allow the script to produce output
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

current_process = None
stdout_queue = Queue()
stderr_queue = Queue()

@app.route('/')
def index():
    sports_data = fetch_all_sports()
    sports = sports_data.get("items", [])
    sports_list = display_sports_options(sports)
    return render_template('index.html', sports=sports_list)

@app.route('/get_leagues', methods=['POST'])
def get_leagues():
    sport_id = request.json.get('sport_id')
    leagues_data = fetch_leagues_for_sport(sport_id)
    leagues = leagues_data.get("items", [])
    leagues_list = display_league_options(leagues)
    return jsonify(leagues_list)

@app.route('/start_scraper', methods=['POST'])
def start_scraper_route():
    sport_id = request.json.get('sport_id')
    league_id = request.json.get('league_id')
    start_date = request.json.get('start_date', '').replace("-", "")
    end_date = request.json.get('end_date', '').replace("-", "")
    if not start_date or not end_date:
        start_date = datetime.now().strftime("%Y%m%d")
        end_date = datetime.now().strftime("%Y%m%d")

    result = run_scraper(sport_id, league_id, start_date, end_date)
    if result:
        file_path, extra_file_path = result
        return jsonify(success=True, file_path=file_path, extra_file_path=extra_file_path)
    else:
        return jsonify(success=False)

@app.route('/get_output', methods=['GET'])
def get_output_route():
    output = get_output()
    print(f"GET request received to fetch output. Output: {output}")
    return jsonify(output)

@app.route('/download/<filename>')
def download_file(filename):
    downloads_dir = os.path.join(app.root_path, 'downloads')
    return send_from_directory(downloads_dir, filename)

if __name__ == '__main__':
    app.run(debug=True)
