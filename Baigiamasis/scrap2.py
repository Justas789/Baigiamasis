import requests
from bs4 import BeautifulSoup
import csv
import time

base_url = 'https://liquipedia.net/easportsfc/'

def get_player_match_pages():
    """Gauti žaidėjų puslapius per puslapius"""
    player_links = set()
    page_number = 1
    
    while True:
        url = f'{base_url}Category:Player_Matches_pages?page={page_number}' 
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/easportsfc/') and '/Matches' in href:
                    cleaned_href = href.replace('/easportsfc/', '/')
                    player_links.add(base_url + cleaned_href.lstrip('/'))  
            
            next_page = soup.find('a', text='(next page')
            if next_page:
                page_number += 1  
            else:
                break  
            
        else:
            print(f'Error fetching page {page_number}: {response.status_code}')
            break
    
    return player_links

def get_player_name(player_url):
    """Ištraukia žaidėjo vardą iš puslapio"""
    response = requests.get(player_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', class_='firstHeading')
        if title:
            player_name = title.get_text(strip=True)
            return player_name
    print(f"Klaida gaunant žaidėjo vardą iš {player_url}")
    return "Nežinomas žaidėjas"

def scrape_player_matches(player_url, writer):
    player_name = get_player_name(player_url)  
    
    response = requests.get(player_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='wikitable')
        
        if table:
            for row in table.find_all('tr')[1:]:  
                cols = row.find_all('td')
                if len(cols) >= 7:
                    date, time, tier, tournament = [cols[i].text.strip() for i in [0, 1, 2, 4]]
                    score = f"{cols[5].get_text(separator=' ').strip()} : {cols[7].get_text(separator=' ').strip()}"
                    opponent = cols[8].get_text(separator=' ').strip()
                    
                    writer.writerow([player_name, date, time, tier, tournament, score, opponent])
                    print(f"Žaidėjas: {player_name}, Data: {date}, Laikas: {time}, Lygis: {tier}, Turnyras: {tournament}, Rezultatas: {score}, Oponentas: {opponent}")
        else:
            print(f"Nerasta rungtynių lentelės žaidėjui: {player_url}")
    else:
        print(f"Klaida gaunant žaidėjo puslapį {player_url}: {response.status_code}")

def main():
    player_urls = get_player_match_pages() 
    
    with open('fifa_all_players_matches.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Žaidėjas', 'Data', 'Laikas', 'Lygis', 'Turnyras', 'Rezultatas', 'Oponentas'])
        
        for player_url in player_urls:
            scrape_player_matches(player_url, writer)
            time.sleep(6) 

if __name__ == '__main__':
    main()
