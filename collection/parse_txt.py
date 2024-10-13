import re
import csv
from datetime import datetime
from os import listdir, getcwd
from os.path import isfile, join

path = join(getcwd().parent, "data", "meta")

files = [f for f in listdir(path) if isfile(join(path, f))]

data = []


def parse_line(line, obj):
    pattern = r'"([^"]+)"\s*:\s*(null|ObjectId\("[^"]+"\)|"[^"]*"|\d+)'
    match = re.match(pattern, line)
    if match:
        key = match.group(1)
        value = match.group(2)

        # Remove quotes from a simple value if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        return key, value
    else:
        return None, None


def structure_data(data):
    imdbId = data.pop("imdbID")
    movie = {"imdbID": imdbId, "Year": year, **data}
    return movie


def parse_file(file, data, year):
    obj = {}
    for line in file:
        line = line.strip()
        if not line:
            continue

        if line == "{":
            obj = {}
            continue

        if line == "}":
            data.append(structure_data(obj))
            continue

        if "ObjectId" in line:
            continue

        key, value = parse_line(line, obj)

        if not key:
            print("Failed to parse line: ", line)
            continue

        if value == "null" or value == "N/A":
            value = None

        if key == "Released" and value:
            parsed_date = datetime.strptime(value, "%d %b %Y")
            value = parsed_date.strftime("%Y-%m-%d")

        if key == "Runtime" and value:
            value = int(value.split(" ")[0])

        obj[key] = value


for file_name in files:
    if file_name == ".DS_Store":
        continue

    file_path = join(path, file_name)
    year = file_name.split(".")[0]
    with open(file_path, "r", encoding="utf-16") as file:
        try:
            parse_file(file, data, year)
        except Exception as e:
            print("Failed to parse file: ", file_name)
            print(e)
            continue


file_name = "data.csv"

fieldnames = data[0].keys()

# Write the list of dictionaries to a CSV file
with open(file_name, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for entry in data:
        writer.writerow(entry)
