import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.topverses.com/Bible/&pg="
TOTAL_VERSES = 300
VERSES_PER_PAGE = 10
TOTAL_PAGES = TOTAL_VERSES // VERSES_PER_PAGE
OUTPUT_FILE = "bibleVerses.ts"
SAVE_RANK = False

def escape_string(s):
    return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ")

def scrape_page(page_num):
    url = f"{BASE_URL}{page_num}"
    print(f"Scraping page {page_num}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    verses = []

    containers = soup.select(".scripture")
    for container in containers:
        reference = container.find("h2").text.strip()
        text_blocks = container.select(".versetext.remove-bottom")
        if not text_blocks:
            print(f"No text blocks found for verse {reference}")
            continue
        text_block = text_blocks[-1]
        if not "KJV" in text_block.text:
            print(f"No KJV text found for verse {reference}")
        rank = container.find("h5").text.split(":")[1].strip()
        verse_text = text_block.text.strip().split("KJV")[0].strip()

        verse_data = {
            "quote": escape_string(verse_text),
            "author": escape_string(reference)
        }

        if SAVE_RANK:
            rank = container.find("h5").text.split(":")[1].strip()
            verse_data["rank"] = rank

        verses.append(verse_data)
    return verses

def main():
    all_verses = []
    for page in range(1, TOTAL_PAGES + 1):
        try:
            verses = scrape_page(page)
            all_verses.extend(verses)
            time.sleep(1)  # polite delay
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    print(f"Scraped {len(all_verses)} verses. Writing to TypeScript file...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("export const bibleVerses = [\n")
        for verse in all_verses:
            if SAVE_RANK:
                f.write(f'  {{ quote: "{verse["quote"]}", author: "{verse["author"]}", rank: "{verse["rank"]}" }},\n')
            else:
                f.write(f'  {{ quote: "{verse["quote"]}", author: "{verse["author"]}" }},\n')
        f.write("];\n")

    print(f"✅ Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
