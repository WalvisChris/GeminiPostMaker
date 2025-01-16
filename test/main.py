from PIL import Image, ImageDraw, ImageFont
import os
import datetime
import requests
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

naam_van_maand = ["JAN", "FEB", "MAA", "APR", "MEI", "JUN", "JUL", "AUG", "SEP", "OKT", "NOV", "DEC"]

def get_saturday() -> str:
    today = datetime.date.today()
    today_weekday = today.weekday()
    days_until_saturday = (5 - today_weekday) % 7
    next_saturday = today + datetime.timedelta(days=days_until_saturday)
    date = next_saturday.day
    month = naam_van_maand[next_saturday.month - 1]
    result = f"ZATERDAG {date} {month}"
    return result

def get_centered_x(draw: ImageDraw, s: str, font: ImageFont) -> int:
    bbox = draw.textbbox((0, 0), s, font=font)
    WIDTH = bbox[2] - bbox[0]
    return int((1080 - WIDTH) / 2)

def draw_match(draw: ImageDraw, image: Image, icon: Image, font_gemini: ImageFont, font_tegenstander: ImageFont, font_info: ImageFont, y: int, thuiswedstrijd: bool, team: str, tegenstander: str, stad: str, tijd: str):
    
    if thuiswedstrijd:
        image.paste(icon, (40, y+25), icon if icon.mode == "RGBA" else None)
        draw.text((170, y), team, fill="yellow", font=font_gemini)
        draw.text((170, y+95), tegenstander, fill="white", font=font_tegenstander)
        draw.text((170, y+215), f"GOUDA - {tijd}", fill="white", font=font_info)
    else:
        image.paste(icon, (40, y+130), icon if icon.mode == "RGBA" else None)
        draw.text((170, y), tegenstander, fill="white", font=font_tegenstander)
        draw.text((170, y+105), team, fill="yellow", font=font_gemini)
        draw.text((170, y+230), f"{stad} - {tijd}", fill="white", font=font_info)

def load_matches():
    matches = []

    url = "https://gemini-korfbal.nl/competitie/"
    response = requests.get(url)

    if response.status_code == 200:
        print("Wedstrijden zijn geladen.")
    else:
        print("Wedstrijden laden mislukt.")
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
    
    return matches

def generate(source: str, icon: str, output: str, matches):
    
    # load
    image = Image.open(source)
    logo = Image.open(icon)

    # resize
    logo_width, logo_height = logo.size
    logo = logo.resize((logo_width // 4, logo_height // 4), Image.Resampling.LANCZOS)

    # draw
    draw = ImageDraw.Draw(image)

    # Fonts
    try:
        path1 = os.path.join(os.getcwd(), "headline.ttf")
        path2 = os.path.join(os.getcwd(), "cairo.ttf")
        path3 = os.path.join(os.getcwd(), "gemini.ttf")
        font_headline = ImageFont.truetype(path1, size=170)
        font_cairo = ImageFont.truetype(path2, size=60)
        font_gemini = ImageFont.truetype(path3, size=100)
        font_tegenstander = ImageFont.truetype(path2, size=80)
        font_info = ImageFont.truetype(path2, size=45)
        font_normal = ImageFont.truetype("arial.ttf", size=50)
    except IOError as e:
        print(f"Font werd niet herkent. Arial wordt gebruikt. {e}")
        font_headline = ImageFont.load_default()
        font_cairo = ImageFont.load_default()
        font_gemini = ImageFont.load_default()
        font_tegenstander = ImageFont.load_default()
        font_info = ImageFont.load_default()
        font_normal = ImageFont.load_default()
    
    # Tekst 1: Headline
    text1 = "WEDSTRIJDEN"
    draw.text((get_centered_x(draw, text1, font_headline), 50), text1, fill="yellow", font=font_headline)

    # Tekst 2: Datum
    text2 = get_saturday()
    draw.text((get_centered_x(draw, text2, font_cairo), 210), text2, fill="white", font=font_cairo)

    # Wedstrijden
    for y, match in enumerate(matches):
        draw_match(draw, image, logo, font_gemini, font_tegenstander, font_info, 450+(y*500), match.isThuisWedstrijd, match.team, match.tegenstander, "N/A", match.tijd)

    # Output
    image.save(output)
    image.show()
    print(f"Foto opgeslagen als: {output}")

# start
wallpaper = "achtergrond.jpg"
resultaat = "wedstrijd.jpg"
logo = "logo.png"

wedstrijden = load_matches()

generate(wallpaper, logo, resultaat, wedstrijden)