import os
import requests
import csv
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

symbol = "IBM"  # Example stock symbol
function = "INCOME_STATEMENT"  # Income Statement endpoint

endpoint_url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}'
response = requests.get(endpoint_url)
data = response.json()

# Check if the request was successful
if "quarterlyReports" in data:
    # Extract the quarterly reports from the response
    quarterly_reports = data["quarterlyReports"]

    # Define CSV file path
    csv_file_path = f"{symbol}_income_statement.csv"

    # Write data to CSV file
    with open(csv_file_path, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=quarterly_reports[0].keys())
        writer.writeheader()
        writer.writerows(quarterly_reports)

    print(f"Data saved to {csv_file_path}")
else:
    print("Error: Failed to fetch data from Alpha Vantage API")
