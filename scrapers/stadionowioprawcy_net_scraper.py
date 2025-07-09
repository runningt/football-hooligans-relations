"""stadionowioprawcy.net scrapper"""

import csv
import os
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://stadionowioprawcy.net"
CLUBS_URL = f"{BASE_URL}/ekipa/"
OUTPUT_DIR = "data"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_club_links():
    """Fetches the list of club links from stadionowioprawcy.net."""

    response = requests.get(CLUBS_URL, timeout=20)
    soup = BeautifulSoup(response.content, "html.parser")
    club_links = []

    # Find all club links
    for link in soup.select('a[href^="/ekipy/"]'):
        club_name = link["href"].split("/")[-1]
        club_links.append(club_name)

    return club_links


def fetch_relations(club_name):
    """Fetches good and bad relations for a given club."""
    response = requests.get(f"{BASE_URL}/ekipy/{club_name}/", timeout=20)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract good relations (ZGODY)
    zgody = []
    zgody_section = soup.find("span", class_="far fa-handshake")
    if zgody_section:
        zgody_list = zgody_section.find_next("p").find_all("a")

    # Extract bad relations (KOSY)
    kosy = []
    kosy_section = soup.find("span", class_="far fa-hand-rock")
    if kosy_section:
        kosy_list = kosy_section.find_next("br").find_next("p").find_all("a")
        for link in kosy_list:
            kosy.append(link.get_text(strip=True))

    # Save to CSV
    output_file = os.path.join(OUTPUT_DIR, f"{club_name}.csv")
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Good Relations (ZGODY)", "Bad Relations (KOSY)"])

        max_length = max(len(zgody), len(kosy))
        for i in range(max_length):
            good_relation = zgody[i] if i < len(zgody) else ""
            bad_relation = kosy[i] if i < len(kosy) else ""
            writer.writerow([good_relation, bad_relation])

    print(f"Saved relations for {club_name} to {output_file}")


def main():
    """main scrapper function"""
    club_links = fetch_club_links()

    # Use ThreadPoolExecutor for parallel scraping
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(fetch_relations, club_links)


if __name__ == "__main__":
    main()
