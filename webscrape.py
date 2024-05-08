import re
# import csv
import json # Switched from CSV to JSON
import sys
import random
import requests
from bs4 import BeautifulSoup

# https://biztoc.com/hot
# https://biztoc.com/light

main_source_URL = "https://biztoc.com/light"
html_name = "web_page.html"

# Scrape list of sources with recent stock-related news.
def get_sources(source_URL):
    print(f"\n[-] Retrieving HTML from: {source_URL}.")

    response = requests.get(source_URL)

    if response.status_code == 200:
        print(f"[✔] Successfully retrieved HTML of size {str(sys.getsizeof(response.text)/(1024 * 1024))[:5]} MB.")
        return response.text, source_URL
    else:
        print(f"[✗] Error: {response.status_code}")

# Parse all available URLs from source HTML.
def get_URLs(source_HTML, source_URL):
    print(f"\n[-] Retrieving all available URLs from: {source_URL}.")

    try:
        soup = BeautifulSoup(source_HTML, 'html.parser')
        anchors_with_href = soup.find_all('a', href=True)
        href_list = [tag['href'] for tag in anchors_with_href]
        href_list_len = len(href_list)

        print(f"[✔] Successfully retrieved {href_list_len} URLs.")
        return href_list, href_list_len

    except Exception as e:
        print(f"[✗] Error: {e}")

# Save all content available in each URL retrieved from source HTML.
def get_content(source_HTML, source_URL):
    print(f"\n[-] Retrieving all available text entries from: {source_URL}.")

    try:
        soup = BeautifulSoup(source_HTML, "html.parser")

        # Retrieve title
        title = soup.title.string.strip()
        print(f"[✔] Title of the HTML file: {title}")

        # Retrieve date
        date = get_date(source_HTML, source_URL)
        if date:
            print(f"[✔] Article date: {date}")
        else:
            print("[✗] Article date not found.")

        # Retrieve text entries
        elements = soup.find_all(["p", "div", "a"])
        filtered_texts = [element.get_text(strip=True) for element in elements if len(element.get_text(strip=True).split()) > 5]
        unique_texts = list(set(filtered_texts))

        data = {
            "source": source_URL,
            "title": title,
            "date": date,
            "paragraphs": unique_texts
        }

        json_path = "content.json"
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        print(f"[✔] Data saved to: {json_path}")

    except Exception as e:
        print(f"[✗] Error: {e}")


def get_date(source_HTML, source_URL):
    print(f"\n[-] Retrieving article date from: {source_URL}.")

    try:
        pattern = r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b"
        regex = re.compile(pattern, re.IGNORECASE)
        match = regex.search(source_HTML)

        if match:
            print(f"[✔] Successfully retrieved article date: {match.group()}.")
            return match.group()
        else:
            print("[✗] Error: Date not found.")
            return None

    except Exception as e:
        print(f"[✗] Error: {e}")
        return None


# Get list of URLs from source HTML.
source_HTML, source_URL = get_sources(main_source_URL)
source_URLs, source_URLs_Length = get_URLs(source_HTML, source_URL)

random_Index = random.randint(1, source_URLs_Length)
print(f"\n[✔] Random index chosen for URL list: {random_Index}")

# Get data and metadata from each individual HTML in the list of URLs.
individual_HTML, individual_URL = get_sources(source_URLs[random_Index])
get_content(individual_HTML, individual_URL)
get_date(individual_URL, individual_URL)

# Terminal space push.
print("\n\n\n\n\n\n")