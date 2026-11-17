import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "static", "samples")
os.makedirs(SAMPLES_DIR, exist_ok=True)

def create_gradient(width, height, color_top, color_bottom):
    """Creates a vertical gradient image."""
    base = Image.new("RGB", (width, height), color_top)
    top = np.array(color_top, dtype=float)
    bot = np.array(color_bottom, dtype=float)
    data = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        factor = y / height
        col = top * (1 - factor) + bot * factor
        data[y, :, :] = col.astype(np.uint8)
    return Image.fromarray(data)

def generate_beach_sunset():
    # 800x500 Beach Sunset
    img = create_gradient(800, 500, (247, 100, 48), (255, 210, 120))
    draw = ImageDraw.Draw(img)
    
    # Sun
    draw.ellipse([340, 180, 460, 300], fill=(255, 245, 180))
    
    # Ocean gradient
    ocean = create_gradient(800, 200, (190, 80, 50), (20, 40, 80))
    img.paste(ocean, (0, 300))
    
    draw = ImageDraw.Draw(img)
    # Sun reflection on water
    for y in range(300, 450, 4):
        w = int(60 + (y - 300) * 0.8)
        draw.line([(400 - w//2, y), (400 + w//2, y)], fill=(255, 220, 130, 150), width=2)
    
    # Shore / Sand
    draw.polygon([(0, 420), (800, 390), (800, 500), (0, 500)], fill=(160, 110, 70))
    
    # Silhouette boat
    draw.polygon([(480, 360), (560, 360), (540, 380), (490, 380)], fill=(30, 20, 20))
    draw.line([(520, 360), (520, 310)], fill=(30, 20, 20), width=3) # Mast
    draw.polygon([(520, 315), (550, 345), (520, 350)], fill=(60, 40, 40)) # Sail
    
    # Silhouette child / figure
    draw.ellipse([215, 365, 227, 377], fill=(25, 15, 20)) # Head
    draw.line([(221, 377), (221, 405)], fill=(25, 15, 20), width=4) # Body
    draw.line([(221, 405), (216, 425)], fill=(25, 15, 20), width=3) # Left leg
    draw.line([(221, 405), (226, 425)], fill=(25, 15, 20), width=3) # Right leg
    draw.line([(221, 385), (232, 395)], fill=(25, 15, 20), width=2) # Arm gesturing
    
    # Flying seagulls
    for sx, sy in [(150, 120), (180, 135), (210, 115), (620, 90), (650, 105)]:
        draw.arc([sx, sy, sx+16, sy+12], 180, 360, fill=(40, 25, 30), width=2)
        draw.arc([sx+14, sy, sx+30, sy+12], 180, 360, fill=(40, 25, 30), width=2)
    
    img.save(os.path.join(SAMPLES_DIR, "beach_sunset.jpg"), quality=95)
    print("Created beach_sunset.jpg")

def generate_enchanted_forest():
    # 800x500 Enchanted Forest
    img = create_gradient(800, 500, (10, 35, 30), (30, 95, 60))
    draw = ImageDraw.Draw(img)
    
    # Sunbeams filtering down
    beam_layer = Image.new("RGBA", (800, 500), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beam_layer)
    for bx in [200, 380, 550, 680]:
        bdraw.polygon([(bx, 0), (bx+40, 0), (bx+180, 500), (bx-20, 500)], fill=(220, 255, 180, 35))
    img.paste(Image.alpha_composite(img.convert("RGBA"), beam_layer).convert("RGB"))
    
    draw = ImageDraw.Draw(img)
    # Tree trunks & canopy
    for tx in [60, 170, 320, 480, 640, 760]:
        w = 32
        draw.polygon([(tx, 500), (tx+w, 500), (tx+w-10, 0), (tx+10, 0)], fill=(15, 25, 20))
        # branches
        draw.line([(tx+15, 220), (tx-40, 160)], fill=(15, 25, 20), width=6)
        draw.line([(tx+20, 180), (tx+70, 130)], fill=(15, 25, 20), width=6)

    # Ancient deer silhouette
    draw.ellipse([395, 365, 430, 390], fill=(20, 30, 22)) # body
    draw.ellipse([425, 345, 442, 365], fill=(20, 30, 22)) # head/neck
    draw.line([(405, 390), (405, 425)], fill=(20, 30, 22), width=3) # legs
    draw.line([(425, 390), (425, 425)], fill=(20, 30, 22), width=3)
    # Antlers
    draw.line([(435, 345), (445, 320)], fill=(20, 30, 22), width=2)
    draw.line([(445, 320), (440, 310)], fill=(20, 30, 22), width=2)
    draw.line([(445, 320), (455, 315)], fill=(20, 30, 22), width=2)

    # Glowing orbs / fireflies
    for fx, fy in [(120, 320), (250, 280), (360, 340), (510, 290), (620, 360), (700, 250), (420, 220)]:
        draw.ellipse([fx-6, fy-6, fx+6, fy+6], fill=(180, 255, 140))

    img.save(os.path.join(SAMPLES_DIR, "enchanted_forest.jpg"), quality=95)
    print("Created enchanted_forest.jpg")

def generate_cyberpunk_city():
    # 800x500 Cyberpunk Metropolis
    img = create_gradient(800, 500, (15, 5, 35), (45, 15, 70))
    draw = ImageDraw.Draw(img)

    # Background Skyscrapers
    buildings = [
        (40, 120, 110), (160, 80, 90), (260, 150, 120), (390, 60, 100),
        (500, 110, 130), (640, 90, 120), (740, 160, 90)
    ]
    for bx, by, bw in buildings:
        draw.rectangle([bx, by, bx+bw, 500], fill=(20, 12, 40))
        # Windows grid
        for wy in range(by + 20, 480, 18):
            for wx in range(bx + 10, bx + bw - 10, 14):
                if (wx + wy) % 7 != 0:
                    win_color = (0, 255, 230) if (wx + wy) % 5 == 0 else ((255, 0, 128) if (wx + wy) % 3 == 0 else (255, 230, 80))
                    draw.rectangle([wx, wy, wx+7, wy+10], fill=win_color)

    # Neon billboards
    draw.rectangle([280, 170, 360, 210], fill=(255, 0, 110))
    draw.rectangle([520, 130, 600, 170], fill=(0, 240, 255))
    
    # Flying vehicles / sky trails
    for vy in [180, 240, 310]:
        draw.line([(50, vy), (750, vy - 20)], fill=(0, 255, 200, 180), width=2)
        draw.ellipse([450, vy-12, 470, vy-4], fill=(255, 255, 255))

    img.save(os.path.join(SAMPLES_DIR, "cyberpunk_city.jpg"), quality=95)
    print("Created cyberpunk_city.jpg")

def generate_ancient_library():
    # 800x500 Historic Library
    img = create_gradient(800, 500, (40, 20, 10), (90, 50, 25))
    draw = ImageDraw.Draw(img)

    # Arched window in the middle
    draw.arc([300, 60, 500, 280], 180, 360, fill=(240, 210, 140), width=4)
    draw.rectangle([300, 170, 500, 330], outline=(240, 210, 140), width=4)
    # Ambient warm glow
    draw.rectangle([304, 170, 496, 326], fill=(255, 235, 170))

    # Bookshelves on sides
    for shelf_x, shelf_w in [(20, 250), (530, 250)]:
        draw.rectangle([shelf_x, 40, shelf_x+shelf_w, 480], fill=(30, 15, 8))
        for sy in range(90, 470, 65):
            draw.rectangle([shelf_x+5, sy, shelf_x+shelf_w-5, sy+8], fill=(60, 35, 15))
            # Book spines
            bx = shelf_x + 10
            while bx < shelf_x + shelf_w - 20:
                bw = np.random.randint(10, 20)
                bh = np.random.randint(40, 55)
                bcol = [(140, 30, 30), (30, 60, 120), (35, 90, 45), (170, 130, 40), (70, 40, 90)][(bx * 7) % 5]
                draw.rectangle([bx, sy - bh, bx + bw, sy], fill=bcol)
                bx += bw + 3

    # Scholar at desk
    draw.rectangle([320, 380, 480, 440], fill=(50, 25, 12)) # desk
    draw.ellipse([385, 340, 415, 370], fill=(25, 15, 10)) # scholar
    draw.ellipse([335, 365, 355, 385], fill=(210, 170, 60)) # brass lamp

    img.save(os.path.join(SAMPLES_DIR, "ancient_library.jpg"), quality=95)
    print("Created ancient_library.jpg")

def generate_mountain_summit():
    # 800x500 Mountain Summit
    img = create_gradient(800, 500, (40, 90, 170), (160, 210, 245))
    draw = ImageDraw.Draw(img)

    # Rolling clouds in middle
    for cy in [260, 300, 330]:
        for cx in range(0, 850, 80):
            draw.ellipse([cx-70, cy-35, cx+70, cy+35], fill=(235, 245, 255))

    # Peaks
    peaks = [
        ([(80, 220), (220, 450), (0, 450)], (90, 105, 125), (245, 250, 255)),
        ([(650, 180), (800, 440), (500, 440)], (80, 95, 115), (245, 250, 255)),
        ([(380, 130), (580, 480), (180, 480)], (60, 75, 95), (255, 255, 255))
    ]
    for pts, rock_col, snow_col in peaks:
        draw.polygon(pts, fill=rock_col)
        # Snow cap
        apex = pts[0]
        snow_poly = [apex, (apex[0]-35, apex[1]+60), (apex[0]+40, apex[1]+60)]
        draw.polygon(snow_poly, fill=snow_col)

    # Lone mountaineer on foreground ridge
    draw.polygon([(0, 440), (320, 390), (450, 500), (0, 500)], fill=(35, 42, 50))
    # Figure
    draw.ellipse([305, 355, 317, 367], fill=(220, 60, 40)) # red jacket hood
    draw.rectangle([306, 367, 318, 385], fill=(220, 60, 40))
    draw.line([(310, 385), (307, 398)], fill=(20, 20, 20), width=2)
    draw.line([(314, 385), (316, 398)], fill=(20, 20, 20), width=2)
    draw.line([(318, 368), (328, 398)], fill=(180, 180, 180), width=2) # walking stick

    img.save(os.path.join(SAMPLES_DIR, "mountain_summit.jpg"), quality=95)
    print("Created mountain_summit.jpg")

def generate_cozy_cafe():
    # 800x500 Cozy Cafe Window
    img = create_gradient(800, 500, (30, 25, 40), (80, 50, 35))
    draw = ImageDraw.Draw(img)

    # Rain streaks on windowpane
    for rx in range(30, 780, 25):
        draw.line([(rx, 0), (rx - 15, 320)], fill=(80, 95, 120, 120), width=2)

    # Window frame
    draw.rectangle([0, 0, 800, 330], outline=(40, 30, 25), width=12)
    draw.line([(400, 0), (400, 330)], fill=(40, 30, 25), width=8)

    # Table in foreground
    draw.rectangle([0, 330, 800, 500], fill=(120, 75, 45))
    draw.line([(0, 330), (800, 330)], fill=(160, 105, 65), width=4)

    # Coffee mug & steam
    draw.ellipse([350, 380, 430, 440], fill=(240, 240, 245))
    draw.ellipse([355, 385, 425, 430], fill=(70, 40, 20)) # coffee liquid
    draw.arc([420, 395, 445, 425], 270, 90, fill=(240, 240, 245), width=4) # handle
    # Steam
    for sx in [380, 400]:
        draw.arc([sx, 330, sx+25, 375], 90, 270, fill=(240, 240, 240), width=2)

    # Journal & pen
    draw.polygon([(470, 390), (570, 380), (580, 450), (480, 460)], fill=(220, 205, 175))
    draw.line([(550, 420), (600, 400)], fill=(20, 20, 20), width=3) # pen

    img.save(os.path.join(SAMPLES_DIR, "cozy_cafe.jpg"), quality=95)
    print("Created cozy_cafe.jpg")

if __name__ == "__main__":
    generate_beach_sunset()
    generate_enchanted_forest()
    generate_cyberpunk_city()
    generate_ancient_library()
    generate_mountain_summit()
    generate_cozy_cafe()
    print("All sample images generated successfully!")
