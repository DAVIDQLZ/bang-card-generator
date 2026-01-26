### CONFIG FILE ###
# Edit the parameters below to customize card generation.
# 1) Save changes to config file.
# 2) Menu -> Config -> Reload config to apply changes.

from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Size and resolution
DPI = 300
CARD_WIDTH_MM = 56
CARD_HEIGHT_MM = 87

SCREEN_SIZE = (800, 600)  # Width, Height in pixels

# Fonts
FONTS = {
    "title": BASE_DIR / "resources" / "fonts" / "title.ttf",
    "subtitle": BASE_DIR / "resources" / "fonts" / "subtitle.ttf",
    "body": BASE_DIR / "resources" / "fonts" / "body.ttf",
}

FONT_SIZES = {
    "title": 77,
    "subtitle": 32,
    "body": 36,
    "value": 50,
    "author": 20,
}

TEXT_COLOR = {
    "title": (0, 0, 0, 255),
    "subtitle": (0, 0, 0, 255),
    "body": (0, 0, 0, 255),
    "value": (0, 0, 0, 255),
    "author": (0, 0, 0, 255),
}

# Paths to templates and suits
TEMPLATES = {
    0: BASE_DIR / "resources" / "templates" / "0_action.png",
    1: BASE_DIR / "resources" / "templates" / "1_blue_item.png",
    2: BASE_DIR / "resources" / "templates" / "2_green_item.png",
    3: BASE_DIR / "resources" / "templates" / "3_character3.png",
    4: BASE_DIR / "resources" / "templates" / "4_character4.png",
    5: BASE_DIR / "resources" / "templates" / "5_character5.png",
    6: BASE_DIR / "resources" / "templates" / "6_character6.png",
}

SUITS = {
    0: BASE_DIR / "resources" / "suits" / "hearts.png",
    1: BASE_DIR / "resources" / "suits" / "clubs.png",
    2: BASE_DIR / "resources" / "suits" / "diamonds.png",
    3: BASE_DIR / "resources" / "suits" / "spades.png",
}

# Vignette
VIGNETTE_FLAG = True
VIGNETTE_COLOR = (255, 255, 255, 255) 
VIGNETTE_MARGIN = 30
VALUE_OUTLINE_WIDTH = 3

# Other paths
BORDER_PATH = BASE_DIR / "resources" / "misc" / "border.png"
BACK_PLAYING_PATH = BASE_DIR / "resources" / "misc" / "back-playing.png"
BACK_CHARACTER_PATH = BASE_DIR / "resources" / "misc" / "back-character.png"
DEFAULT_ART_PATH = BASE_DIR / "resources" / "misc" / "default-art.png"
DEFAULT_EXP_ART_PATH = BASE_DIR / "resources" / "misc" / "krtek.png"

# README file path
README_PATH = BASE_DIR / "README.md"



