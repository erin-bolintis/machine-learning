import csv
import json
import html
from fnmatch import fnmatch
from datetime import datetime
from os import listdir, getcwd
from os.path import isfile, join

from matplotlib.font_manager import json_dump

path = join(getcwd(), "data", "json")

files = [f for f in listdir(path) if isfile(join(path, f))]

data = []


def parse_duration(duration):
    hours = 0
    minutes = 0

    duration = duration.replace("PT", "")

    if "H" in duration:
        hours = int(duration.split("H")[0])
        duration = duration.split("H")[1]

    if "M" in duration:
        minutes = int(duration.split("M")[0])
        duration = duration.split("M")[1]

    minutes = minutes + (hours * 60)

    return minutes


def parse_item(raw, file_name):
    item = {}
    item["id"] = file_name.split(".")[0]
    item["type"] = raw["@type"]
    item["title"] = html.unescape(raw["name"]).replace(";", ":")
    item["genre"] = raw.get("genre", None)

    if "description" in raw:
        item["description"] = html.unescape(raw["description"]).replace(";", ":")
    else:
        item["description"] = None
    item["published_at"] = raw.get("datePublished", None)
    item["content_rating"] = raw.get("contentRating", None)

    if "aggregateRating" in raw:
        item["rating_value"] = raw["aggregateRating"]["ratingValue"]
        item["rating_count"] = raw["aggregateRating"]["ratingCount"]
    else:
        item["rating_value"] = None
        item["rating_count"] = None

    if "duration" in raw:
        item["duration"] = parse_duration(raw["duration"])
    else:
        item["duration"] = None

    item["keywords"] = raw.get("keywords", "").split(",")
    item["directors"] = [
        html.unescape(director["name"]) for director in raw.get("director", [])
    ]
    item["actors"] = [html.unescape(actor["name"]) for actor in raw.get("actor", [])]

    return item


for file_name in files:
    if not fnmatch(file_name, "*.json"):
        continue

    with open(join(path, file_name), "r") as f:
        json_string = json.load(f)

        try:
            item = parse_item(json_string, file_name)
            data.append(item)
        except Exception as e:
            print(e)
            print(json.dumps(json_string, indent=2))
            break

file_name = join("data", "metadata.csv")

fieldnames = data[0].keys()

# Write the list of dictionaries to a CSV file
with open(file_name, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for entry in data:
        writer.writerow(entry)
