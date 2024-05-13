import re
import sys
import json
import spacy
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

#________________________________________________________________________________________________________________________________________________________________

# Current Issues: Content parsing from get_text() is only returning entries if it contains a words with a length of 15+.

#________________________________________________________________________________________________________________________________________________________________

# https://biztoc.com/hot
# https://biztoc.com/light

main_source_URL = "https://biztoc.com/light"
html_name = "web_page.html"

#________________________________________________________________________________________________________________________________________________________________

# Scrape list of sources with recent stock-related news.
def get_sources(source_URL: str, source_URLs = [], retry = False):
    print(f"\n[-] Retrieving HTML from: {source_URL}. (Retry Mode: {retry})")

    response = requests.get(source_URL)

    if response.status_code == 200:
        print(f"[✔] Successfully retrieved HTML of size {str(sys.getsizeof(response.text)/(1024 * 1024))[:5]} MB.")
        return response.text, source_URL

    elif response.status_code >= 400 and response.status_code < 600 and retry == True:
        print(f"[-] Retry Mode: Initial response is {response.status_code}. Retrying with different URLs from source HTML.")
        for new_URL in source_URLs:
            if len(new_URL) > 10:
                new_response = requests.get(new_URL)
                if new_response.status_code == 200:
                    print(f"[✔] Successfully retrieved HTML of size {str(sys.getsizeof(response.text)/(1024 * 1024))[:5]} MB.")
                    return new_response.text, new_URL
        print(f"[✗] Error: A 200-ranged response of was not received.")

    else:
        print(f"[✗] Error: {response.status_code}.")

#________________________________________________________________________________________________________________________________________________________________

# Parse all available URLs from source HTML.
def get_URLs(source_HTML: str, source_URL: str):
    print(f"\n[-] Retrieving all available URLs from: {source_URL}.")

    try:
        soup = BeautifulSoup(source_HTML, 'html.parser')
        anchors_with_href = soup.find_all('a', href=True)
        href_list = [tag['href'] for tag in anchors_with_href]
        href_list_len = len(href_list)

        print(f"[✔] Successfully retrieved {href_list_len} URLs.")
        return href_list, href_list_len

    except Exception as e:
        print(f"[✗] Error: {e}.")

#________________________________________________________________________________________________________________________________________________________________

# Save all content available in each URL retrieved from source HTML.
def get_content(source_HTML: str, source_URL: str):
    print(f"\n[-] Retrieving available data from: {source_URL}.")

    #____________________________________________________________

    def get_title():
        try:
            title = soup.title.string.strip()
            if title:
                print(f"[✔] Article title: {title}")
                return title
            else:
                print(f"[✗] Article Title not found.")

        except Exception as e:
            print(f"[✗] Error: {e}.")

    def get_date():
        try:
            pattern = r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b"
            regex = re.compile(pattern, re.IGNORECASE)
            match = regex.search(source_HTML)

            if match:
                print(f"[✔] Article date: {match.group()}.")
                return match.group()
            else:
                print(f"[✗] Article date not found.")

        except Exception as e:
            print(f"[✗] Error: {e}.")


    def get_text():
        try:
            elements = soup.find_all(["p", "div", "a"])
            word_threshold = 20
            similarity_threshold = 0.4
            blacklist = None
            blacklist_path = "./blacklist.txt"

            with open(blacklist_path, "r") as file:
                blacklist = file.read().splitlines()

            texts = [
                element.get_text(strip=True)
                for element in elements
                if (
                    len(element.get_text(strip=True).split()) >= word_threshold
                    # and not any(word in element.get_text(strip=True) for word in blacklist)
                )
            ]
            unique_texts = [texts[0]]
            vectorizer = TfidfVectorizer()

            for text in texts[1:]:
                duplicate = False
                for unique_text in unique_texts:
                    similarity = cosine_similarity(
                        vectorizer.fit_transform([text, unique_text])
                    )
                    if similarity[0][1] > similarity_threshold:
                        duplicate = True
                        break
                if not duplicate:
                    unique_texts.append(text)

            if unique_texts:
                print(f"[✔] Article text: {len(unique_texts)} paragraphs.")
                return unique_texts
            else:
                print(f"[✗] Article text not found.")

        except Exception as e:
            print(f"[✗] Error: {e}.")

    #____________________________________________________________

    try:
        soup = BeautifulSoup(source_HTML, "html.parser")

        data = {
            "source": source_URL,
            "title": get_title(),
            "date": get_date(),
            "paragraphs": get_text(),
        }

        file_path = "content.json"
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        print(f"[✔] Article data saved to: {file_path}.")
        return file_path

    except Exception as e:
        print(f"[✗] Error: {e}.")

#________________________________________________________________________________________________________________________________________________________________

# Current time in 12 hour interval format.
def curr_time():
    return datetime.now().strftime("%I:%M:%S %p")

#________________________________________________________________________________________________________________________________________________________________

# Append identified company name from the saved JSON file.
def get_company(entries: str, file_path: str):
    print(f"\n[-] Identifying name from: {file_path}.")

    try:
        en_model = spacy.load("en_core_web_sm")
        entries_prime = en_model(entries)

        for entities in entries_prime.ents:
            print(entities.text, entities.label_)

    except Exception as e:
        print(f"[✗] Error: {e}.")

#________________________________________________________________________________________________________________________________________________________________

def main():
    try:
        print(f"\nSTAGE 1 [{curr_time()}] ░░░░░░░░░░░░░░░░░░░░░░░░░░░")

        # Get list of URLs from source HTML.
        source_HTML, source_URL = get_sources(main_source_URL)
        source_URLs, source_URLs_Length = get_URLs(source_HTML, source_URL)

        #____________________________________________________________

        print(f"\nSTAGE 2 [{curr_time()}] ░░░░░░░░░░░░░░░░░░░░░░░░░░░")

        # Picks random HTML for testing purposes.
        random_Index = random.randint(1, source_URLs_Length)
        print(f"\n[✔] Random index chosen for URL list: {random_Index}.")

        # Get data and metadata from each individual HTML in the list of URLs.
        individual_HTML, individual_URL = get_sources(source_URLs[random_Index], source_URLs=source_URLs, retry=True)
        file_path = get_content(individual_HTML, individual_URL)

        #____________________________________________________________

        print(f"\nSTAGE 3 [{curr_time()}] ░░░░░░░░░░░░░░░░░░░░░░░░░░░")

        # Get company name from JSON file.
        get_company("sample text", file_path)

        # Terminal space push.
        print("\n\n\n\n\n\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()