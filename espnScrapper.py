import requests
import pandas as pd


def fetch_scoreboard_data(sport):
    # Base URL for the ESPN API
    base_url = "http://site.api.espn.com/apis/site/v2/sports"
    url = f"{base_url}/{sport}/scoreboard"
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

def display_league_options(leagues):
    print("Available league options:")
    for league in leagues:
        print(f"{league['id']}: {league['name']}")

if __name__ == '__main__':
    try:
        leagues = sport_leagues_data.get('leagues', [])
        display_league_options(leagues)
        sport = input("Enter the sport (e.g., baseball/mlb, football/nfl, basketball/nba): ").strip().lower()
        json_data = fetch_scoreboard_data(sport)
        games = parse_scoreboard(json_data)
        if games:
            filename = f"{sport.replace('/', '_')}_scoreboard.csv"
            save_scoreboard_to_csv(games, filename)
        else:
            print("No scoreboard data found.")
    except requests.RequestException as e:
        print(f"Failed to fetch data from ESPN API. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
