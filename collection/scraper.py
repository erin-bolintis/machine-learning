import csv
import json
import os
from fnmatch import fnmatch
from os import listdir, getcwd
from os.path import isfile, join
from time import sleep
from playwright.sync_api import sync_playwright


def scrape_imdb(imdb_id):
    url = f"https://www.imdb.com/title/{imdb_id}/"

    # Launch Playwright in synchronous mode
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        # Navigate to the URL
        page.goto(url, wait_until="domcontentloaded")

        page.wait_for_load_state("load")

        # Extract the JSON Linked Data
        json_ld = page.query_selector("script[type='application/ld+json']")
        if json_ld:
            json_data = json_ld.inner_text()
            data = json.loads(json_data)

            path = join(getcwd(), "data", "json", f"{imdb_id}.json")
            with open(path, "w") as f:
                json.dump(data, f)
        else:
            print("JSON Linked Data not found.")

        # Close the browser
        browser.close()


root = join(getcwd(), "data", "posters")
pattern = "*.jpg"

posters = []

for path, subdirs, files in os.walk(root):
    for name in files:
        if fnmatch(name, pattern):
            imdb_id = name.split(".")[0]
            posters.append(imdb_id)


path = join(getcwd(), "data", "json")
json_files = [f for f in listdir(path) if isfile(join(path, f))]

for j in json_files:
    imdb_id = j.split(".")[0]
    if imdb_id in posters:
        posters.remove(imdb_id)


# # Scrape the IMDb page for each value in the list
for index, imdb_id in enumerate(posters):
    try:
        scrape_imdb(imdb_id)
    except Exception as e:
        print(f"Error: {e}")
        sleep(120)

    print(f"Scraped: {index}/{len(posters)}")
