import os
import re
import json
import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup

class Match:
    def __init__(self, atHome: bool, home: str, away: str, city: str, time: str):
        self.atHome = atHome
        self.home = home
        self.away = away
        self.city = city
        self.time = time

    def __str__(self):
        return f"{self.home} vs {self.away} - {self.time}"

def next_saturday_string() -> str:
    today = datetime.date.today()
    today_weekday = today.weekday()
    days_until_saturday = (5 - today_weekday) % 7
    next_saturday = today + datetime.timedelta(days=days_until_saturday)
    date = next_saturday.day
    month = month_to_string[next_saturday.month - 1]
    result = f"ZATERDAG {date} {month}"
    return result

def get_centered_x(draw: ImageDraw, text: str, font: ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    WIDTH = bbox[2] - bbox[0]
    return int((1080 - WIDTH) / 2)

def draw_match(image: Image, draw: ImageDraw, y: int, atHome: bool, team: str, away: str, city: str, time: str) -> None:
    if atHome:
        image.paste(logo, (40, y+25), logo if logo.mode == "RGBA" else None)
        draw.text((170, y), team, fill="yellow", font=font_gemini)
        draw.text((170, y+95), away, fill="white", font=font_enemy)
        draw.text((170, y+215), f"GOUDA - {time}", fill="white", font=font_info)
    else:
        image.paste(logo, (40, y+130), logo if logo.mode == "RGBA" else None)
        draw.text((170, y), away, fill="white", font=font_enemy)
        draw.text((170, y+105), team, fill="yellow", font=font_gemini)
        draw.text((170, y+230), f"{city} - {time}", fill="white", font=font_info)

def load_matches(date: str):
    matches = []
    url = "https://gemini-korfbal.nl/competitie/"
    response = requests.get(url)

    if response.status_code == 200:
        print(get_succes("Wedstrijden zijn gevonden."))
    else:
        print(get_error("Wedstrijden konden niet worden ingeladen."))
        exit()

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("tr")
    for row in rows[1:]:
        
        cells = row.find_all("td")
        if len(cells) > 1:

            date_str = cells[0].get_text(strip=True)
            if date_str == date:

                time = cells[1].get_text(strip=True)
                team1 = cells[2].get_text(strip=True)
                team2 = cells[3].get_text(strip=True)

                if "Gemini" in team1:
                    atHome = True
                    team = team1
                    away = team2
                    city = "GOUDA"
                else:
                    atHome = False
                    team = team2
                    away = team1
                    city = get_city_for_team(away)

                match = Match(atHome, team.upper(), away, city, time)
                matches.append(match)
                print(get_debug(f"Loaded match: {match}"))
    
    return matches

def generate_result(image: Image, index: int) -> Image:
    new_image = image.copy()
    draw = ImageDraw.Draw(new_image)

    headline = "WEDSTRIJDEN"
    draw.text((get_centered_x(draw, headline, font_headline), 50), headline, fill="yellow", font=font_headline)

    info = next_saturday_string()
    draw.text((get_centered_x(draw, info, font_info), 210), info, fill="white", font=font_info)

    amount_of_matches_on_this_post = 3 if len(matches) - (index * 3) >= 3 else len(matches) % 3

    print(get_debug(f"'amount_of_matches_on_this_post' is {amount_of_matches_on_this_post} for post {index+1}"))

    for i in range(amount_of_matches_on_this_post):
        match = matches[index * 3 + i]
        draw_match(new_image, draw, 450+(i*500), match.atHome, match.home, match.away, match.city, match.time)

        print(get_debug(f"drawing match {match} to post {index+1}"))

    return new_image

def normalize_team_name(team_name: str) -> str:
    team_name = re.sub(r"/.*", "", team_name)
    team_name = team_name.split()[0]
    team_name = re.sub(r"\s*\d+\s*", "", team_name)
    normalized_name = team_name.lower()
    return normalized_name

def get_city_for_team(team_name: str):
    normalized_team_name = normalize_team_name(team_name)
    city = cities.get(normalized_team_name, None)
    
    if city is None:
        print(get_error(f"Stad voor '{team_name}' niet gevonden."))
        city = str(input(get_error(f"Voer de stad voor '{team_name}' in: "))).upper()

    return city

def get_error(s: str) -> str:
    return "[\033[31mERROR\033[0m] " + s

def get_succes(s: str) -> str:
    return "[\033[92mSUCCES\033[0m] " + s

def get_debug(s: str) -> str:
    return "[\033[33mDEBUG\033[0m] " + s

month_to_string = ["JAN", "FEB", "MAA", "APR", "MEI", "JUN", "JUL", "AUG", "SEP", "OKT", "NOV", "DEC"]
cities = {}
logo = None
font_headline = None
font_gemini = None
font_enemy = None
font_info = None

# start
os.system('cls')

with open("res/city.json", "r") as json_file:
    cities = json.load(json_file)
    print(get_succes("Steden geladen."))

datum = str(input("Voer de gewenste datum in (dd-mm-jjjj): "))
matches = load_matches(datum)
print(get_succes(str(len(matches)) + " wedstrijden zijn geladen."))

# Images
source = Image.open("res/achtergrond.jpg")
logo = Image.open("res/logo.png")
logo_width, logo_height = logo.size
logo = logo.resize((logo_width // 4, logo_height // 4), Image.Resampling.LANCZOS)

# Fonts
try:
    font_headline = ImageFont.truetype(os.path.join(os.getcwd(), "res/fonts/headline.ttf"), size=170)
    font_gemini = ImageFont.truetype(os.path.join(os.getcwd(), "res/fonts/gemini.ttf"), size=100)
    font_enemy = ImageFont.truetype(os.path.join(os.getcwd(), "res/fonts/cairo.ttf"), size=80)
    font_info = ImageFont.truetype(os.path.join(os.getcwd(), "res/fonts/cairo.ttf"), size=45)
except IOError as e:
    print(get_error(f"Lettertypen konden niet geladen worden: ({e})"))
    font_headline = ImageFont.load_default()
    font_gemini = ImageFont.load_default()
    font_enemy = ImageFont.load_default()
    font_info = ImageFont.load_default()

# Make posts
posts = len(matches) // 3
if len(matches) % 3 != 0:
    posts += 1

print(get_debug(f"making {posts} posts."))

for i in range(posts):
    result_image = generate_result(source, i)
    result_image.save(f"posts/wedstrijden_{i+1}.jpg")
    result_image.show()
    print(get_succes(f"Post opgeslagen als 'wedstrijden_{i+1}.jpg' in 'posts'"))