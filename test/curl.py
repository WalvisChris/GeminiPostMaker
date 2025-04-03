import requests
import datetime
from bs4 import BeautifulSoup

class Match:
    def __init__(self, isThuisWedstrijd: bool, team: str, tegenstander: str, stad: str, tijd: str):
        self.isThuisWedstrijd = isThuisWedstrijd
        self.team = team
        self.tegenstander = tegenstander
        self.stad = stad
        self.tijd = tijd

    def __str__(self):
        return f"Thuis: {self.isThuisWedstrijd}, Team: {self.team}, Tegenstander: {self.tegenstander}, Stad: {self.stad}, Tijd: {self.tijd}"

matches = []

url = "https://gemini-korfbal.nl/competitie/"
response = requests.get(url)
if response.status_code == 200:
    print("ja")
else:
    print("fout")
    exit()

soup = BeautifulSoup(response.text, "html.parser")
rows = soup.find_all("tr")
for row in rows[1:]:
    cells = row.find_all("td")
    if len(cells) > 1:
        
        today = datetime.date.today()
        days_until_saturday = (5 - today.weekday()) % 7
        next_saturday = today + datetime.timedelta(days=days_until_saturday)
        date_str = cells[0].get_text(strip=True)
        match_date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()

        if match_date == next_saturday:

            tijd = cells[1].get_text(strip=True)
            team1 = cells[2].get_text(strip=True)
            team2 = cells[3].get_text(strip=True)

            if "Gemini" in team1:
                isThuisWedstrijd = True
                team = team1
                tegenstander = team2
            else:
                isThuisWedstrijd = False
                team = team2
                tegenstander = team1

            match = Match(isThuisWedstrijd, team.upper(), tegenstander, "Onbekend", tijd)
            matches.append(match)

for match in matches:
    print(match)