import os
import requests
import csv
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
symbol = "IBM"
function = "TIME_SERIES_DAILY"

endpoint_url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}'
response = requests.get(endpoint_url)
data = response.json()

if "Time Series (Daily)" in data:
    daily_data = data["Time Series (Daily)"]
    csv_file_path = f"{symbol}_daily_data.csv"

    with open(csv_file_path, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["Date", "Open", "High", "Low", "Close", "Volume"])
        writer.writeheader()
        for date, values in daily_data.items():
            writer.writerow({
                "Date": date,
                "Open": values["1. open"],
                "High": values["2. high"],
                "Low": values["3. low"],
                "Close": values["4. close"],
                "Volume": values["5. volume"]
            })

    print(f"Data saved to {csv_file_path}")
else:
    print("Error: Failed to fetch data from Alpha Vantage API")
