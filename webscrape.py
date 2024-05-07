import csv
import requests
from bs4 import BeautifulSoup

# https://biztoc.com/hot
# https://biztoc.com/light

main_source_URL = "https://biztoc.com/light"
html_name = "web_page.html"

# Scrape list of sources with recent stock-related news.
def get_sources(source_URL):

    response = requests.get(source_URL)

    if response.status_code == 200:
        print(f"HTML file saved from: {source_URL}.")
        return response.text
    else:
        print(f"Error: {response.status_code}")

# Parse all available URLs from source HTML.
def get_URLs(source_HTML):

    soup = BeautifulSoup(source_HTML, 'html.parser')
    anchors = soup.find_all('a')
    href_list = [tag.get('href') for tag in anchors]

    print("Source URLs parsed from HTML.")
    return href_list

# Save all content available in each URL retrieved from source HTML.
def get_content(source_HTML):

    soup = BeautifulSoup(source_HTML, "html.parser")

    paragraphs = soup.find_all("p", class_=False)
    paragraph_lists = [p.get_text(strip=True) for p in paragraphs]

    csv_path = "content.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Paragraph"])
        writer.writerows([[p_text] for p_text in paragraph_lists])

    print(f"Paragraphs saved to: {csv_path}.")

source_HTML = get_sources(main_source_URL)
source_URLs = get_URLs(source_HTML)
individual_HTML = get_sources(source_URLs[1])
get_content(individual_HTML[1])
# extra