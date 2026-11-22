"""Draw the 22 November front page with Pillow."""
from functools import lru_cache
from math import cos, dist, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAPER, RED, NAVY = "#F7F3E8", "#9E2B25", "#1F3552"
INK, GRAY, GOLD = "#21252A", "#51565C", "#E8D9A8"
SEA = "#DCE8EE"

HEROES = [
    ("1 · KUWAIT · BAHRAIN · GULF WAR", "Iran strikes US bases in the Gulf",
     "Missiles and drones hit a US air base in Kuwait and targets in Bahrain, where an industrial facility was struck; two tankers were hit near Hormuz.", "— Reuters · AP"),
    ("2 · ANTALYA · CLIMATE", "COP31 spills into overtime, near a deal",
     "A new draft text lands after fossil-fuel rows; the presidency says it can win every party's approval as talks run past their close.", "— AFP · UN News"),
    ("3 · KYIV · CRIMEA · WAR", "Zelensky calls the Crimea Bridge strike 'fair'",
     "Ukraine says the bridge hit answers Russia's barrage; Moscow hits Kyiv's bridges and rail yards and strikes Zelensky's home city.", "— Reuters · France 24"),
]

TILES = [
    ("4 · HONG KONG · POLITICS", "Hong Kong votes for its Election Committee", "Some 5,700 voters pick the 1,500-strong college."),
    ("5 · WELLINGTON · CRICKET", "India declare on 720/9, a record", "Pant hits 128 as India pile up their best in NZ."),
    ("6 · MEXICO · CARTELS", "Mexico captures 'El Chapo Isidro'", "Top drug lord taken in a string of arrests."),
    ("7 · JERUSALEM · POLITICS", "Herzog taps Eisenkot to form a government", "Ex-army chief gets the nod over Netanyahu."),
    ("8 · LVIV · WAR", "Russian strike on Lviv kills two", "Missile hits a building; ten more injured."),
    ("9 · GENEVA · ARMS", "No deal on 'killer robot' rules", "UN talks end agreeing only to keep talking."),
    ("10 · RIYADH · WAR", "Houthis attack Riyadh", "Three ballistic missiles intercepted, Saudis say."),
    ("11 · BRUSSELS · BUDGET", "Costa proposes a €1.78tn EU budget", "Seven-year plan for 2028–34 heads to summit."),
    ("12 · WASHINGTON · TECH", "Trump tells Nvidia: bring back Huang", "President demands the ousted chief's return."),
    ("13 · TURIN · TENNIS", "Alcaraz meets Zverev for the title", "ATP Finals decider closes the season."),
]

BRIEFS = """14 TALLINN — Estonia moves to shut its Russia border. Reuters
15 WARSAW — War spills into Poland in a missile claim. Reuters
16 CARACAS — US details $12bn in Venezuelan oil and mineral revenue. AP
17 OTTAWA — Hegseth memo curbs the US–Canada defence tie. Reuters
18 GAZA — Four nations press Israel to let aid reach flooded Gaza. AFP
19 PARIS — France marks a fourth weekend of cost-of-living protests. AFP
20 LIMA — Peru quake leaves 152 homes uninhabitable. Reuters
21 LONDON — France reach the Nations Championship final vs South Africa. AFP
22 MASTUNG — 15 terrorists killed in a Balochistan operation. State media
23 JAKARTA — 39 missing after a candy-factory fire. Local reports
24 HORMUZ — Two tankers struck near the strait; Iran readies 14 to defy the blockade. Reuters
25 WASHINGTON — Shutdown fight deepens as the Iran war splits lawmakers. AP
26 TUPANCIRETÃ — Supercell storm kills three in southern Brazil. The Straits Times
27 NEW YORK — GTA VI's day-one sales hit $4.9bn; Nvidia faces an accounting probe. Manila Times
28 BRAZIL — Dengue-fighting mosquitoes show strong new evidence. The Straits Times
29 MOUNTAIN VIEW — Google puts Duplex into Gemini App Tasks. The Verge
30 SEATTLE — AWS launches a distributed KV-cache agent skill. AWS
31 WASHINGTON — FinCEN flags MEXC; Binance may hold its deposits. PANews
32 SINGAPORE — AI agent verification protocol and stablecoin sandbox planned. PANews
33 DOHA — Pakistan beat UAE by 61 runs in the Rising Stars Asia Cup. AP
34 ISLAMABAD — Pakistan–Indonesia finish a joint anti-terror drill. News wires
35 LONDON — Copper posts its worst week of 2026. BeInCrypto
36 KYIV — Russia hits railway stations as well as bridges. Reuters
37 KRYVYI RIH — Russia strikes Zelensky's home city; 58 hurt. France 24""".splitlines()

CONTINENTS = [
    [(-168,66),(-140,70),(-125,72),(-110,73),(-95,80),(-85,66),(-75,62),(-65,60),(-55,52),(-60,45),(-70,42),(-75,35),(-80,25),(-85,30),(-95,20),(-105,20),(-110,25),(-120,35),(-125,48),(-140,60),(-155,58),(-165,60)],
    [(-80,10),(-75,5),(-70,0),(-60,-5),(-50,-5),(-40,-10),(-35,-15),(-40,-25),(-50,-30),(-60,-35),(-70,-40),(-75,-50),(-70,-55),(-75,-35),(-80,-20),(-80,-5)],
    [(-10,35),(0,35),(10,37),(20,32),(30,31),(35,28),(40,20),(45,12),(50,10),(45,0),(40,-10),(35,-20),(30,-30),(20,-35),(15,-30),(10,-15),(5,0),(0,5),(-10,10),(-15,25)],
    [(-10,36),(-5,40),(0,43),(5,45),(10,55),(15,58),(20,60),(25,65),(30,70),(35,68),(30,60),(25,55),(20,50),(15,45),(10,40),(5,38),(0,36)],
    [(35,70),(50,72),(70,73),(90,75),(110,76),(130,72),(150,70),(170,66),(160,60),(150,55),(140,45),(130,40),(120,35),(110,25),(100,20),(95,10),(90,5),(85,15),(80,20),(75,25),(70,30),(60,30),(55,25),(50,30),(45,35),(40,40),(35,45),(35,55),(40,60)],
    [(113,-22),(120,-15),(130,-12),(140,-17),(145,-15),(150,-22),(150,-30),(145,-38),(140,-38),(130,-32),(120,-35),(113,-30)],
]
LOCATIONS = [
    (52,32),(28,38),(33,52),(114,22),(175,-41),(-102,23),(35,32),(25,47),(6,46),
    (45,24),(7,54),(-77,39),(10,43),(28,62),(19,54),(-67,10),(-76,45),(28,27),
    (-3,44),(-77,-12),(-4,54),(67,30),(107,-6),(58,24),(-84,33),(-54,-29),
    (-74,41),(-52,-15),(-122,37),(-122,47),(-69,44),(104,1),(51,25),(73,33),
    (-3,53),(39,44),
]

FONTS = {"sans": "Sans", "bold": "Sans-Bold", "serif": "Serif",
         "title": "Serif-Bold", "italic": "Serif-Italic"}


@lru_cache
def font(face, size):
    file = f"/usr/share/fonts/truetype/dejavu/DejaVu{FONTS.get(face, "Sans")}.ttf"
    if face == "condensed":
        file = "/usr/share/fonts/truetype/noto/NotoSans-Condensed.ttf"
    if face == "italic" and not Path(file).is_file():
        file = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
    return ImageFont.truetype(file, size)


def wrap(text, face, width):
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if current and face.getlength(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    return lines + [current]


def block(draw, box, text, face, size, color=INK, max_lines=1, minimum=8, align="left"):
    x, y, width, height = box
    for point in range(size, minimum - 1, -1):
        f = font(face, point)
        lines = wrap(text, f, width)
        step = point if face == "condensed" else point + 1
        bounds = [f.getbbox(line) for line in lines]
        top = min(b[1] for b in bounds)
        bottom = max(i * step + b[3] for i, b in enumerate(bounds))
        if len(lines) <= max_lines and bottom - top <= height and all(
            max(f.getlength(line), b[2]) - min(0, b[0]) <= width
            for line, b in zip(lines, bounds)
        ):
            break
    else:
        raise AssertionError(f"Text does not fit {box}: {text}")
    for i, (line, b) in enumerate(zip(lines, bounds)):
        span = max(f.getlength(line), b[2]) - min(0, b[0])
        offset = {"left": 0, "center": (width - span) / 2, "right": width - span}[align]
        assert 0 <= offset and offset + span <= width + 0.001
        assert 0 <= i * step + b[1] - top <= i * step + b[3] - top <= height
        draw.text((x + offset - min(0, b[0]), y + i * step - top), line, fill=color, font=f)


def tracked(draw, x, y, text, right=False):
    f = font("bold", 10)
    width = sum(f.getlength(c) for c in text) + 1.35 * (len(text) - 1)
    x = x - width if right else x
    assert 24 <= x and x + width <= 1000.001
    for c in text:
        draw.text((x, y), c, font=f, fill=RED, anchor="lt")
        x += f.getlength(c) + 1.35


def artwork(image, x, y, width, height, kind):
    """Illustrate on a local canvas, then scale into the column."""
    w, h = 320, 128 if kind <= 3 else 72
    palettes = [
        ("#182941","#42667A"), ("#D9E4D6","#829B91"), ("#D7D8CD","#718794"),
        ("#D8E5EB","#829DA9"), ("#CFD9B0","#7F9662"), ("#25384E","#677C8A"),
        ("#DCE4E6","#99AFBD"), ("#D8C6B7","#917C77"), ("#CEDFE9","#789EAE"),
        ("#182941","#4D677C"), ("#1D385E","#355982"), ("#233E43","#547A70"),
        ("#9ABEAD","#477D75"),
    ]
    sky, ground = palettes[kind - 1]
    canvas = Image.new("RGB", (w, h), sky)
    d = ImageDraw.Draw(canvas)
    line, rect, poly, oval = d.line, d.rectangle, d.polygon, d.ellipse

    def skyline(base, color):
        for i in range(18):
            left = i * 19
            high = 7 + (i * 13 % 27)
            rect((left, base - high, left + 15, base), fill=color)
            for win in range(base - high + 5, base, 7):
                line((left + 3, win, left + 6, win), fill=ground)

    def waves(start):
        rect((0, start, w, h), fill=ground)
        for i in range(26):
            xx = (i * 41) % w
            yy = start + 4 + i * 13 % (h - start - 4)
            line((xx, yy, xx + 8 + i % 17, yy), fill=sky)

    def smoke(x0, y0, color):
        for i in range(7):
            dx, dy = x0 + i * 4, y0 - i * 5
            oval((dx - i, dy - i, dx + 9 + i, dy + 8 + i), fill=color)

    def burst(x0, y0, radius):
        points = []
        for i in range(16):
            a = i * pi / 8
            r = radius if i % 2 == 0 else radius / 3
            points.append((x0 + r * cos(a), y0 + r * sin(a)))
        poly(points, fill="#F4BD6D")
        oval((x0-2, y0-2, x0+2, y0+2), fill=PAPER)

    if kind == 1:
        for yy in range(85):
            line((0, yy, w, yy), fill=(18 + yy // 6, 31 + yy // 4, 51 + yy // 4))
        oval((278, 12, 299, 33), fill="#F4E9CC")
        oval((283, 18, 288, 22), fill="#DFD4BB")
        oval((291, 25, 295, 28), fill="#DFD4BB")

        for origin, control, target in [
            ((0, 3), (58, -1), (99, 68)),
            ((319, 0), (248, 1), (227, 67)),
        ]:
            trail = []
            for i in range(33):
                t = i / 32
                trail.append(tuple((1-t)**2*a + 2*t*(1-t)*b + t*t*c
                                   for a, b, c in zip(origin, control, target)))
            line(trail, fill="#A3B0BB", width=2)
            line(trail[-12:], fill="#F3C69A", width=2)

        rect((0, 85, w, h), fill="#101E32")
        for i in range(38):
            xx = i * 47 % w
            yy = 89 + i * 17 % 38
            line((xx, yy, xx + 6 + i % 16, yy), fill="#293F56")
        line((0, 85, w, 85), fill="#637584")

        for bx, by in [(99, 68), (227, 67)]:
            poly([(bx-43, 85), (bx-33, 80), (bx+26, 80), (bx+37, 85)],
                 fill="#101726")
            poly([(bx-31, 80), (bx-31, 74), (bx-23, 68), (bx-14, 68),
                  (bx-6, 74), (bx-6, 80)], fill="#101726")
            rect((bx+7, 73, bx+25, 81), fill="#101726")
            line((bx+18, 73, bx+18, 63), fill="#101726", width=2)
            line((bx+13, 65, bx+23, 65), fill="#101726")
            oval((bx-9, by-9, bx+9, by+9), fill="#805642")
            burst(bx, by, 8)
            line((bx+11, 76, bx+14, 76), fill="#EAA45F")

        # A low cargo deck and a lit bridge give the tanker a clear profile.
        poly([(77, 105), (244, 105), (228, 119), (89, 119)], fill="#080F1B")
        poly([(80, 110), (238, 110), (234, 114), (83, 114)], fill="#A93D43")
        line((78, 105, 242, 105), fill="#B2A695", width=2)
        rect((94, 93, 119, 104), fill="#C8C4B8")
        rect((98, 88, 115, 93), fill="#E3DCC7")
        line((106, 88, 106, 82), fill="#D5CCB6")
        for xx in (101, 107, 113):
            rect((xx, 95, xx+2, 97), fill="#433D39")
        line((129, 101, 218, 101), fill="#88909A", width=2)
        for xx in range(131, 221, 14):
            line((xx, 102, xx, 105), fill="#88909A")
            line((xx, 103, xx+3, 103), fill="#F5D791", width=2)
        for xx, yy, length in [(73, 121, 42), (142, 122, 29), (206, 120, 37)]:
            line((xx, yy, xx+length, yy), fill="#587084")
    elif kind == 2:
        for xx in range(10, w, 37):
            line((xx, 0, xx, 79), fill=ground, width=2)
        rect((0, 84, w, h), fill=ground)
        oval((111, 9, 193, 91), fill="#407586", outline=NAVY, width=2)
        d.arc((128, 9, 177, 91), 0, 360, fill="#87ABA8")
        d.arc((111, 29, 193, 72), 0, 360, fill="#87ABA8")
        poly([(125, 26), (145, 16), (156, 26), (144, 38), (136, 39), (142, 48), (128, 43)], fill=GOLD)
        poly([(160, 37), (183, 27), (188, 43), (171, 48), (171, 61), (159, 74), (150, 55)], fill=GOLD)
        d.rounded_rectangle((185, 22, 198, 75), radius=6, fill=PAPER, outline=NAVY)
        oval((182, 66, 201, 85), fill=RED)
        line((191, 42, 191, 76), fill=RED, width=5)
        rect((15, 16, 101, 35), fill=RED)
        block(d, (21, 21, 74, 10), "OVERTIME", "bold", 12, PAPER, align="center")
        for xx in range(21, 320, 40):
            oval((xx, 92, xx + 13, 105), fill=NAVY)
            d.rounded_rectangle((xx-4, 104, xx+17, 122), radius=4, fill=NAVY)
        rect((0, 118, w, h), fill="#5D746C")
    elif kind == 3:
        skyline(71, "#78868A")
        waves(72)
        for start, end in [(0, 142), (187, 319)]:
            line((start, 76, end, 76), fill=PAPER, width=7)
            line((start, 80, end, 80), fill=NAVY, width=3)
            for xx in range(start + 20, end - 7, 44):
                rect((xx, 82, xx + 5, 109), fill=NAVY)
                d.arc((xx, 81, xx + 48, 111), 180, 360, fill=NAVY, width=2)
        poly([(137,72),(154,76),(148,81),(159,85),(143,87),(135,81)], fill=NAVY)
        poly([(187,72),(176,80),(183,83),(175,91),(195,82)], fill=NAVY)
        smoke(158, 68, "#6D6D6B")
        smoke(167, 71, "#565B62")
        burst(158, 80, 7)
    elif kind == 4:
        skyline(65, ground)
        rect((118, 34, 203, 68), fill=NAVY)
        poly([(118,34),(131,24),(193,24),(203,34)], fill="#4F718F")
        line((140, 30, 181, 30), fill=INK, width=3)
        poly([(145,8),(174,4),(180,26),(151,31)], fill=PAPER)
        line([(153, 17), (159, 21), (169, 11)], fill=RED, width=2)
    elif kind == 5:
        poly([(0,64),(320,51),(320,72),(0,72)], fill=ground)
        rect((132, 11, 264, 59), fill="#263D33", outline=GOLD, width=2)
        block(d, (141, 20, 114, 30), "720/9", "bold", 31, PAPER, align="center")
        poly([(64,60),(82,26),(91,30),(77,65),(69,68)], fill=GOLD)
        line((87, 27, 98, 7), fill=NAVY, width=5)
        oval((97, 53, 109, 65), fill=RED)
    elif kind == 6:
        for xx, color in [(15, "#D36C66"), (252, "#75ABC8")]:
            poly([(xx,12),(xx+55,12),(xx+77,65),(xx-15,65)], fill=color)
        for xx in (119, 177):
            oval((xx, 17, xx+35, 54), outline=GOLD, width=5)
            rect((xx+11, 15, xx+23, 25), fill=GOLD)
        for xx in (148, 158, 168):
            oval((xx, 17, xx+13, 25), outline=GOLD, width=2)
    elif kind == 7:
        rect((76, 30, 230, 63), fill=PAPER)
        poly([(69,31),(153,12),(237,31)], fill=NAVY)
        for xx in range(87, 225, 21):
            rect((xx, 34, xx+7, 60), fill=ground)
        line((64, 64, 243, 64), fill=NAVY, width=3)
        line((251, 8, 251, 63), fill=NAVY, width=2)
        rect((252, 8, 286, 28), fill=PAPER)
        for yy in (11, 24):
            line((253, yy, 285, yy), fill="#345E9B", width=2)
        for angle in (0, pi):
            pts = [(269+5*cos(angle+pi/2+i*2*pi/3), 18+5*sin(angle+pi/2+i*2*pi/3)) for i in range(3)]
            line(pts + pts[:1], fill="#345E9B")
    elif kind == 8:
        skyline(69, ground)
        poly([(100,66),(100,18),(139,18),(147,33),(163,21),(169,34),(185,30),(185,66)], fill=NAVY)
        for xx in (109, 121, 165, 175):
            for yy in (39, 52):
                rect((xx, yy, xx+5, yy+7), fill=GOLD)
        smoke(148, 34, "#666974")
        poly([(87,68),(112,58),(137,66),(157,57),(174,68),(203,61),(221,72),(83,72)], fill="#504E52")
    elif kind == 9:
        for xx in (63, 219):
            line((xx, 10, xx, 67), fill=NAVY, width=2)
            rect((xx+1, 11, xx+39, 34), fill="#5C9BC0")
            oval((xx+13, 15, xx+28, 30), outline=PAPER)
            d.arc((xx+17, 15, xx+24, 30), 0, 360, fill=PAPER)
            line((xx+13, 22, xx+28, 22), fill=PAPER)
        d.rounded_rectangle((130, 10, 191, 45), radius=8, fill=NAVY)
        rect((152, 44, 168, 52), fill=NAVY)
        d.rounded_rectangle((116, 50, 205, 77), radius=9, fill=NAVY)
        for xx in (144, 170):
            oval((xx, 23, xx+7, 29), fill=SEA)
    elif kind == 10:
        skyline(71, "#111D2C")
        for xx, yy in [(90, 25), (170, 13), (242, 31)]:
            line((xx-36, yy+22, xx, yy), fill="#B7CDD5", width=2)
            line((xx+32, yy+16, xx, yy), fill="#B77966", width=2)
            burst(xx, yy, 11)
    elif kind == 11:
        for i in range(12):
            a = i * pi / 6
            cx, cy = 86 + 27*cos(a), 36 + 27*sin(a)
            pts = [(cx+(3.6 if j%2==0 else 1.5)*cos(j*pi/5-pi/2),
                    cy+(3.6 if j%2==0 else 1.5)*sin(j*pi/5-pi/2)) for j in range(10)]
            poly(pts, fill=GOLD)
        block(d, (123, 17, 141, 36), "€1.78tn", "title", 30, PAPER, align="center")
    elif kind == 12:
        rect((0, 0, w, h), fill="#152C3A")
        for yy in range(8, 69, 12):
            line([(0, yy), (46, yy), (61, 36 + (yy-36)//2), (259, 36 + (yy-36)//2),
                  (274, yy), (319, yy)], fill="#345765", width=2)
        for xx in range(89, 241, 12):
            rect((xx, 4, xx+4, 15), fill="#E8AD45")
            rect((xx, 56, xx+4, 67), fill="#E8AD45")
            line((xx+1, 5, xx+1, 66), fill="#FFE3A0")
        for yy in range(20, 55, 8):
            rect((68, yy, 84, yy+3), fill="#FFD477")
            rect((236, yy, 252, yy+3), fill="#FFD477")
        d.rounded_rectangle((80, 12, 240, 59), radius=6, fill="#090F24",
                            outline="#73869D", width=2)
        d.rounded_rectangle((86, 17, 234, 54), radius=4, outline="#344B67")
        rect((97, 23, 123, 49), fill="#173C59", outline="#4385A0")
        rect((101, 27, 119, 45), fill="#247B9A")
        rect((105, 31, 115, 41), fill="#67D9E8")
        rect((108, 34, 112, 38), fill="#E3FFFF")
        block(d, (129, 26, 99, 22), "HUANG", "bold", 24, "#FFFFFF", align="center")
    else:
        poly([(53,64),(98,9),(211,9),(260,64)], fill=ground, outline=PAPER)
        line((76, 37, 235, 37), fill=PAPER)
        line((154, 9, 156, 64), fill=PAPER)
        d.arc((132, 13, 153, 40), 40, 280, fill=GOLD, width=3)
        d.arc((162, 13, 185, 40), 250, 505, fill=GOLD, width=3)
        poly([(143,13),(174,13),(172,29),(160,42),(155,42),(145,29)], fill=GOLD)
        rect((155, 40, 161, 51), fill=GOLD)
        rect((145, 51, 172, 56), fill=GOLD)

    image.paste(canvas.resize((width, height), Image.Resampling.LANCZOS), (x, y))


def draw_panel(draw, image, x, story, kind):
    width = 312
    kicker, headline, deck, source = story
    artwork(image, x, 194, width, 116, kind)
    block(draw, (x, 317, width, 12), kicker, "bold", 12, RED)
    block(draw, (x, 333, width, 52), headline, "title", 25, NAVY, 2)
    block(draw, (x, 385, width, 34), deck, "sans", 11, INK, 3, 10)
    block(draw, (x, 422, width, 12), source, "sans", 11, GRAY)


def draw_banner(draw, image, x, y, story, kind):
    width = 184
    kicker, headline, deck = story
    artwork(image, x, y, width, 41, kind)
    block(draw, (x, y+46, width, 10), kicker, "bold", 10, RED)
    block(draw, (x, y+60, width, 33), headline, "bold", 15, NAVY, 2)
    block(draw, (x, y+94, width, 11), deck, "condensed", 10, INK, minimum=9)


def draw_map(draw, x, y, width, height):
    def project(lon, lat):
        return x + (lon + 180) / 360 * width, y + (90 - lat) / 180 * height

    draw.rectangle((x, y, x + width, y + height), fill=SEA, outline=NAVY)
    for lon in range(-150, 180, 30):
        draw.line((project(lon, 89), project(lon, -89)), fill="#C3D5DE")
    for lat in range(-60, 90, 30):
        draw.line((project(-179, lat), project(179, lat)), fill="#C3D5DE")
    for continent in CONTINENTS:
        draw.polygon([project(*point) for point in continent], fill=GOLD, outline=NAVY)
    for island in [[(172,-34),(177,-37),(175,-41),(172,-39)],
                   [(173,-41),(171,-45),(166,-47),(168,-44)],
                   [(96,5),(105,-5),(113,-8),(105,-8)],
                   [(109,1),(114,7),(118,5),(116,-4),(110,-4)]]:
        draw.polygon([project(*point) for point in island], fill=GOLD, outline=NAVY)

    centres = []
    origins = []
    for point in LOCATIONS:
        origin = tuple(round(value) for value in project(*point))
        origins.append(origin)
        for radius in range(45):
            offsets = [(dx, dy) for dx in range(-radius, radius+1)
                       for dy in range(-radius, radius+1) if max(abs(dx), abs(dy)) == radius]
            offsets.sort(key=lambda offset: (dist((0, 0), offset), offset))
            candidate = next(((origin[0]+dx, origin[1]+dy) for dx, dy in offsets
                              if x+5 <= origin[0]+dx <= x+width-5
                              and y+5 <= origin[1]+dy <= y+height-5
                              and all(dist((origin[0]+dx, origin[1]+dy), other) >= 11
                                      for other in centres)), None)
            if candidate is not None:
                centres.append(candidate)
                break
        else:
            raise AssertionError("Unable to position map marker")
    separation = min(dist(a, b) for i, a in enumerate(centres) for b in centres[i+1:])
    assert separation >= 10
    for origin, center in zip(origins, centres):
        if dist(origin, center) > 5:
            draw.line((origin, center), fill=RED)
    for number, (cx, cy) in zip([*range(1, 36), 37], centres):
        draw.ellipse((cx-5, cy-5, cx+5, cy+5), fill=RED)
        block(draw, (cx-5, cy-3, 10, 7), str(number), "bold", 7, PAPER, minimum=7, align="center")
    print(f"Map markers: {len(centres)}, minimum separation {separation:.2f}px")


def render():
    image = Image.new("RGB", (1024, 1024), PAPER)
    draw = ImageDraw.Draw(image)
    rule = lambda y: draw.line((24, y, 999, y), fill=NAVY)

    tracked(draw, 24, 24, "THE WORLD IN ONE DAY")
    tracked(draw, 1000, 24, "37 STORIES · 6 REGIONS · ALL FROM THIS ONE DAY", right=True)
    rule(39)
    block(draw, (24, 45, 976, 62), "Sunday 22 November 2026", "title", 62, NAVY)
    block(draw, (24, 110, 976, 19),
          "Iran hits US bases in the Gulf · COP31 nears a deal in overtime · India declare on 720/9 in Wellington · Zelensky calls the Crimea Bridge strike 'fair'",
          "italic", 17, RED)
    rule(130)

    regions = [("MIDDLE EAST", 5), ("EUROPE", 11), ("AMERICAS", 12),
               ("ASIA", 7), ("OCEANIA", 1), ("GLOBAL", 1)]
    assert sum(count for _, count in regions) == len(HEROES) + len(TILES) + len(BRIEFS) == 37
    stats = [
        ("$12bn", "Venezuelan oil and mineral revenue, detailed by the US"),
        ("720/9", "India's record Test total in Wellington"),
        ("€1.78tn", "Costa's proposed EU budget, 2028–34"),
        ("6.7", "Magnitude of the Peru Andes quake"),
        ("39", "Missing after the Jakarta candy-factory fire"),
        ("$4.9bn", "GTA VI's day-one sales"),
    ]
    for i, ((region, count), (value, label)) in enumerate(zip(regions, stats)):
        x = 24 + i * 163
        draw.rectangle((x, 135, x+155, 147), fill=RED if i == 0 else NAVY)
        block(draw, (x+4, 137, 148, 9), f"{region}  {count}", "bold", 10, PAPER, align="center")
        block(draw, (x, 151, 155, 23), value, "title", 26, NAVY, align="center")
        block(draw, (x+3, 174, 149, 19), label, "sans", 9, GRAY, 2, align="center")

    for i, story in enumerate(HEROES):
        x = 24 + 332 * i
        if i:
            draw.line((x-10, 194, x-10, 431), fill="#A5A39D")
        draw_panel(draw, image, x, story, i+1)
    rule(436)
    for i, story in enumerate(TILES):
        draw_banner(draw, image, 24 + i % 5 * 198, 443 + i // 5 * 111, story, i+4)
    rule(550)
    rule(662)

    block(draw, (24, 670, 436, 15), "WHERE IT HAPPENED", "bold", 14, NAVY)
    draw_map(draw, 24, 689, 438, 228)
    block(draw, (24, 923, 438, 11), "3 also marks story 36 in Kyiv", "sans", 10, GRAY)
    draw.line((470, 670, 470, 935), fill="#A5A39D")
    block(draw, (480, 670, 520, 15), "ALSO ON SUNDAY 22 NOVEMBER 2026", "bold", 14, NAVY)
    for i in range(0, len(BRIEFS), 2):
        x = 480 + (i // 12) * 264
        y = 689 + (i % 12) * 20
        draw.rectangle((x-2, y-1, x+254, y+18), fill="#EEE9DE")
    for i, brief in enumerate(BRIEFS):
        x = 480 + (i // 12) * 264
        y = 689 + (i % 12) * 20
        number, content = brief.split(" ", 1)
        block(draw, (x, y, 16, 11), number, "bold", 10, RED)
        block(draw, (x+19, y, 235, 20), content, "condensed", 10, INK, 2, 9)

    draw.rectangle((24, 937, 999, 982), outline=RED)
    block(draw, (33, 943, 112, 15), "DATE CHECK ✓", "bold", 12, RED)
    block(draw, (148, 943, 841, 36),
          "Every story on this page happened, or was first reported, on Sunday 22 November 2026. LEFT OUT AS EARLIER NEWS: the Shenzhen summit and its joint declaration, the World Court's Myanmar genocide ruling, Anthropic's Nasdaq debut, the GTA VI launch (19 Nov — the $4.9bn day-one sales figure was first reported today), the EU–Indonesia signing and the Sparta II fire (21 Nov).",
          "sans", 11, INK, 3)
    block(draw, (24, 989, 976, 11),
          "Claims are attributed, not stated as fact · Pictures and map: original, drawn in code · Sources: Reuters, AP, AFP, BBC, France 24, SCMP, The Straits Times, UN News, AWS, PANews, BeInCrypto, The Verge, Manila Times · 2026-11-22",
          "sans", 10, GRAY)
    return image


if __name__ == "__main__":
    output = Path(__file__).with_name("entry.png")
    render().save(output, optimize=True)
    size = output.stat().st_size
    with Image.open(output) as saved:
        assert saved.format == "PNG" and saved.size == (1024, 1024)
        saved.verify()
    assert size < 1_048_576
    print(f"{output.name}: 1024 × 1024, {size:,} bytes; all text fits")
