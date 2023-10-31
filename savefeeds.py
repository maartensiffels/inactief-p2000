import os
import csv
import pytz
import feedparser
from datetime import datetime

# Functie om CSV-bestand aan te maken als het niet bestaat
def create_csv_file(file_name):
    if not os.path.exists(file_name):
        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Discipline", "Titel", "Beschrijving", "Publicatiedatum", "Publicatietijd"])

# Zorg ervoor dat de data-directory bestaat
if not os.path.exists('data'):
    os.makedirs('data')

# Lijst van disciplines en bijbehorende RSS-feeds
disciplines = {
    'brandweer': 'https://alarmeringen.nl/feeds/discipline/brandweer.rss',
    'politie': 'https://alarmeringen.nl/feeds/discipline/politie.rss',
    'ambulance': 'https://alarmeringen.nl/feeds/discipline/ambulance.rss',
    'knrm': 'https://alarmeringen.nl/feeds/discipline/knrm.rss',
    'trauma': 'https://alarmeringen.nl/feeds/discipline/trauma.rss'
}

# Huidige datum en tijd
now = datetime.now()
current_year = now.year
current_month = now.month

# Bestandsnamen gebaseerd op het huidige jaar en de huidige maand
all_time_file = 'data/alarmeringen.csv'
current_year_file = f'data/alarmeringen_{current_year}.csv'
current_month_file = f'data/alarmeringen_{current_year}_{current_month}.csv'

# Maak de CSV-bestanden aan
create_csv_file(all_time_file)
create_csv_file(current_year_file)
create_csv_file(current_month_file)

# Verzamel de data
new_guids = set()
for discipline, url in disciplines.items():
    feed = feedparser.parse(url)
    for entry in feed.entries:
        guid = entry.guid
        new_guids.add(guid)

        # Laden van bestaande GUIDs voor deze uitvoering
        existing_guids = set()
        if os.path.exists('existing_guids.txt'):
            with open('existing_guids.txt', 'r') as f:
                existing_guids = set(f.read().splitlines())
        
        # Alleen nieuwe berichten opslaan
        if guid not in existing_guids:
            title = entry.title
            description = entry.get('description', 'Geen beschrijving beschikbaar')
            
            # Tijd omzetten naar lokale tijd in Nederland
            pub_date_utc = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            amsterdam = pytz.timezone('Europe/Amsterdam')
            pub_date_local = pub_date_utc.astimezone(amsterdam)
            pub_date_str = pub_date_local.strftime("%Y-%m-%d")
            pub_time_str = pub_date_local.strftime("%H:%M:%S")

            pub_year = pub_date_local.year
            pub_month = pub_date_local.month

            # Schrijf de nieuwe regel naar de diverse CSV-bestanden
            for file_name in [all_time_file, current_year_file if pub_year == current_year else None, current_month_file if pub_year == current_year and pub_month == current_month else None]:
                if file_name:
                    with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow([discipline, title, description, pub_date_str, pub_time_str])

# Update de lijst met bestaande GUIDs
with open('existing_guids.txt', 'w') as f:
    for guid in new_guids:
        f.write(f"{guid}\n")
