import requests
import pandas as pd
import re
from datetime import datetime


def fetch_all_sports():
    url = "https://sports.core.api.espn.com/v2/sports?limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    return response.json()

def fetch_leagues_for_sport(sports_id):
    url = f"http://sports.core.api.espn.com/v2/sports/{sports_id}/leagues?limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    return response.json()

def fetch_scoreboard_data(sport, league, start_date, end_date):
    url = f"http://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard?limit=1000&dates={start_date}-{end_date}"
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    return response.json()

def parse_scoreboard(json_data):
    games = []

    for event in json_data.get('events', []):
        game_data = {}

        # Extract team names and scores
        competitions = event.get('competitions', [])
        if competitions:
            competitors = competitions[0].get('competitors', [])
            if competitors:
                game_data['Away Team'] = competitors[0].get('team', {}).get('displayName', 'N/A')
                game_data['Away Score'] = competitors[0].get('score', 'N/A')
                game_data['Home Team'] = competitors[1].get('team', {}).get('displayName', 'N/A')
                game_data['Home Score'] = competitors[1].get('score', 'N/A')

        # Extract game status
        status = event.get('status', {}).get('type', {}).get('description', 'N/A')
        game_data['Status'] = status

        if game_data:
            games.append(game_data)

    return games


def save_scoreboard_to_csv(games, filename):
    df = pd.DataFrame(games)
    df.to_csv(filename, index=False)
    print(f"Scoreboard data saved to {filename}")


def extract_sport_id(sport_url):
    match = re.search(r"sports/([^?]+)", sport_url)
    return match.group(1) if match else None

def extract_league_id(league_url):
    match = re.search(r"leagues/([^?]+)", league_url)
    return match.group(1) if match else None

def display_sports_options(sports):
    print("Available sports:")
    for sport in sports:
        sport_id = extract_sport_id(sport['$ref'])
        if sport_id:
            print(f"Sport: {sport_id}")

def display_league_options(leagues):
    print("Available leagues:")
    for league in leagues:
        league_id = extract_league_id(league['$ref'])
        if league_id:
            print(f"League: {league_id}")


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
    df.to_csv(filename, index=False)
    print(f"Extra Data exported to {filename}")

if __name__ == '__main__':
    try:
        sports_data = fetch_all_sports()
        sports = sports_data.get("items", 0)
        display_sports_options(sports)
        if not sports:
            print("No sports data found.")
        else:
            # for entering sport the user wants data for
            sport_id = input("Enter the sport ID from the list above: ").strip().lower()

            # for entering league the user wants data for based on the sport they selected
            leagues_data = fetch_leagues_for_sport(sport_id)
            leagues = leagues_data.get("items", 0)
            display_league_options(leagues)
            league_id = input("Enter the league ID from the list above: ").strip().lower()

            start_date = input("Enter the start date in the format YYYY-MM-DD: ").strip().replace("-", "")
            end_date = input("Enter the end date in the format YYYY-MM-DD: ").strip().replace("-", "")
            json_data = fetch_scoreboard_data(sport_id, league_id, start_date, end_date)
            games = parse_scoreboard(json_data)
            if games:
                filename = f"{sport_id}_{league_id}_scoreboard.csv"
                save_scoreboard_to_csv(games, filename)
            else:
                print("No scoreboard data found.")

            data = fetch_scoreboard_data(sport_id, league_id, start_date, end_date)
            events = data.get('events', [])
            parsed_data = parse_events_data(events)
            export_to_csv(parsed_data, f'Extra_{sport_id}_{league_id}_events_data.csv')

    except requests.RequestException as e:
        print(f"Failed to fetch data from ESPN API. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
