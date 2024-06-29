# scraper.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re

all_dataframes = []

WEBSITE = input(f'Paste the website to scrape: ')
# WEBSITE = "https://mcla.us/schedule/2024-03?page=3"
WEBSITE = "https://espn.com/pll/scoreboard"
EXPORT_NAME = input("Give the scraped data file name: ")
EXPORT_NAME = "new"
COLUMNS = input("Enter comma separated list of desired column headers: ")
# columns = ['Date', 'Time', 'Location', 'away_team_id', 'home_team_id', 'score']
# Date, Time, Location, away_team_id, home_team_id, score
COLUMNS = "Date, Time, Location, away_team_id, home_team_id, score"


def separate_string(input_string):
    # Use regex to split by commas and/or spaces
    separated_list = re.split(r'[,\s]+', input_string)
    # Remove any empty strings that might occur due to multiple spaces or commas
    separated_list = [item for item in separated_list if item]
    return separated_list


COLUMNS = separate_string(COLUMNS)


def fetch_table_data():
    url = WEBSITE  # Change to the actual URL you need to scrape
    response = requests.get(url)
    return response.text


def parse_table(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')  # Adjust this if there are multiple tables or a specific id/class is needed

    data = []
    for row in table.find_all('tr'):
        cols = [ele.text.strip() for ele in row.find_all('td')]
        data.append(cols)
    return data


expected_num_columns = len(COLUMNS)


def standardize_dataframe(df):
    current_num_columns = len(df.columns)
    if current_num_columns < expected_num_columns:
        # Calculate how many columns are missing
        missing_columns = expected_num_columns - current_num_columns

        # Add the missing columns filled with "N/A"
        for i in range(missing_columns):
            df[f'Column_{current_num_columns + i + 1}'] = "N/A"

    return df

def convert_to_dataframe(table_data):
    # if table_data:
    #     raise ValueError("The provided table is empty.")

    columns = COLUMNS
    # Assuming table_data is a list of rows, and each row is a list of cell values
    table_data.pop(0)  # Remove the first row which contains the headers
    table_data = [row[1:] for row in table_data]
    # table_data = [row[:-1] for row in table_data]
    dataframe = pd.DataFrame(table_data)
    standardize_dataframe(dataframe)
    while True:
        try:
            dataframe.columns = columns
            break  # Exit the loop if processing is successful
        except ValueError as ve:
            print(f"\nError: {ve}")
            newColInput = input(
                "You did not have the correct number of column headers enter a new list of desired column headers: ")
            columns = separate_string(newColInput)
    dataframe.to_csv(f'{EXPORT_NAME}.csv', index=False)
    return dataframe

if __name__ == '__main__':
    try:
        all_dataframes.clear()  # Clear the list before appending new data frames.
        html_content = fetch_table_data()
        table_data = parse_table(html_content)
        new_df = convert_to_dataframe(table_data)
        all_dataframes.append(new_df)
        print(f'\nYour file {EXPORT_NAME}.csv has been completed.')
    except requests.RequestException as e:
        print(f"Failed to fetch data from the website. Error: {e}")
    except ValueError as ve:
        print(f"Error processing data: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}. Table could not be loaded.")
