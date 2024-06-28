import requests
import pandas as pd
import re


def fetch_all_sports():
    url = "https://sports.core.api.espn.com/v2/sports"
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    return response.json()


def fetch_leagues_for_sport(sport_url):
    response = requests.get(sport_url)
    response.raise_for_status()  # Ensure we notice bad responses
    return response.json()


def fetch_scoreboard_data(sport, league):
    url = f"http://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
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


def display_sports_options(sports):
    print("Available sports:")
    for sport in sports:
        sport_id = extract_sport_id(sport['$ref'])
        if sport_id:
            print(f"Sports: {sport_id}")


def display_league_options(leagues):
    print("Available leagues:")
    for league in leagues:
        print(f"- {league['name']} (ID: {league['id']})")


if __name__ == '__main__':
    try:
        sports_data = fetch_all_sports()
        sports = sports_data.get("items", 0)
        display_sports_options(sports)
        if not sports:
            print("No sports data found.")
        else:
            display_sports_options(sports)
            sport_id = input("Enter the sport ID from the list above: ").strip().lower()

            selected_sport = next((s for s in sports if extract_sport_id(s['$ref']).lower() == sport_id), None)
            if not selected_sport:
                print("Invalid sport selection. Please select a valid sport ID from the list.")
            else:
                leagues_data = fetch_leagues_for_sport(selected_sport['$ref'])
                leagues = leagues_data.get('leagues', [])

                if not leagues:
                    print(f"No leagues found for the sport: {selected_sport['name']}")
                else:
                    display_league_options(leagues)
                    league_id = input("Enter the league ID from the list above: ").strip().lower()

                    selected_league = next((l for l in leagues if l['id'].lower() == league_id), None)
                    if not selected_league:
                        print("Invalid league selection. Please select a valid league ID from the list.")
                    else:
                        json_data = fetch_scoreboard_data(sport_id, league_id)
                        games = parse_scoreboard(json_data)
                        if games:
                            filename = f"{sport_id}_{league_id}_scoreboard.csv"
                            save_scoreboard_to_csv(games, filename)
                        else:
                            print("No scoreboard data found.")
    except requests.RequestException as e:
        print(f"Failed to fetch data from ESPN API. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
