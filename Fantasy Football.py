from espn_api.football import League

# Replace with your actual league ID and year
# league_id = 264508544
# league_id = 1632848969
league_id = 1299313824
# league_id = 1515680872
year = 2024
# espn_s2 = 'AEA%2BJSWFS%2FX09VN7l%2BeE5KWHrsnjN8anqoPJV97zBdmtM2rPTgfJqHO3yRKQHXOoafzU9IRXk7h9kkPcTx3UgoW47QruGvG7UmVYroWPeah%2ByXItkFhfXMUEo%2FQ7Qfvt5eKN9AbCgP2Napb3AB91HRA45nRy9u7d8D59JyXBKEu5IdruQXIz2ALa9aoMyS2Fu1M6NKq5OAPXFnKE9SqwSdTJGhv4IHWR20Z2Eho6XnEkC7%2Fgxh6Vn4VgXVKWq8gZHZ6ZNju1xGi3%2B6S3P%2B5wTnSdiP04Z8fOU4nrNDRODAFPKGrfLZpevgkWrIJvp7YcwVDhrAJTnYty9r%2FvOX9b1pR4'
# swid = '{9D62F573-9AED-46C1-A463-959C0AFBEF48}'
# Initialize the league
league = League(league_id=league_id, year=year)

# Initialize the league with authentication
# league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

# Print league information
print(f"League Name: {league.settings.name}")
# print(f"Scoring Type: {league.settings.scoringType}")
print(f"Number of Teams: {len(league.teams)}\n")

# Loop through the teams and print information
# for team in league.teams:
#     print(f"Team Name: {team.team_name}")
#     print(f"Wins: {team.wins}, Losses: {team.losses}, Ties: {team.ties}")
#     print("-" * 40)

# Example: Get the top player in free agency
free_agents = league.free_agents(size=10)
print("\nTop 10 Free Agents:")
for player in free_agents:
    print(f"{player.name} - {player.position}")
print()
# Specify the week you're interested in
week = 5  # Replace with the desired week number

# league.power_rankings(week=13)

# Initialize variables to track the team with the least points
least_points = None
team_with_least_points = None

# Loop through each team to get their score for the specified week
for team in league.teams:
    team_score = team.scores[week - 1]  # week - 1 because list indices start at 0
    print(f"{team.team_name} scored {team_score} points in week {week}")

    if least_points is None or team_score < least_points:
        least_points = team_score
        team_with_least_points = team

# Print the team with the least points
if team_with_least_points:
    print(
        f"\nThe team with the least points in week {week} is {team_with_least_points.team_name} with {least_points} points.")
else:
    print("No teams found for the specified week.")

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.keys import Keys
# import time
#
# # Set up your league ID and year
# league_id = 264508544
# year = 2024
#
# # Path to your ChromeDriver
# chrome_driver_path = "/Applications/Google Chrome.app"
#
# # Initialize the WebDriver
# service = Service(executable_path=chrome_driver_path)
# driver = webdriver.Chrome(service=service)
#
# try:
#     # Open ESPN login page
#     driver.get("https://www.espn.com/login")
#
#     # Wait for the page to load
#     time.sleep(5)
#
#     # Find the username and password fields and login button
#     username_field = driver.find_element(By.ID, "disneyid-username")
#     password_field = driver.find_element(By.ID, "disneyid-password")
#     login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
#
#     # Enter your login credentials
#     username_field.send_keys("")
#     password_field.send_keys("")
#
#     # Click the login button
#     login_button.click()
#
#     # Wait for the login process to complete
#     time.sleep(10)
#
#     # Navigate to the league's homepage to ensure cookies are set
#     league_url = f"https://fantasy.espn.com/football/team?leagueId={league_id}&seasonId={year}"
#     driver.get(league_url)
#
#     # Wait for the page to load and cookies to be set
#     time.sleep(5)
#
#     # Retrieve cookies
#     cookies = driver.get_cookies()
#
#     # Extract espn_s2 and SWID
#     espn_s2 = None
#     swid = None
#
#     for cookie in cookies:
#         if cookie['name'] == 'espn_s2':
#             espn_s2 = cookie['value']
#         if cookie['name'] == 'SWID':
#             swid = cookie['value']
#
#     # Print the values
#     print(f"espn_s2: {espn_s2}")
#     print(f"SWID: {swid}")
#
# finally:
#     # Close the browser
#     driver.quit()