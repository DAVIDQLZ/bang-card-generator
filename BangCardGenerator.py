import random
import textwrap
import tkinter as tk
from tkinter import filedialog, ttk, Canvas
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageTk,
)

import config

def generate_card(card_type, art, cardValue, cardSuit, title, subtitle, author, description, backCardFlag, expansionArt, return_pil):
    ### 1. SETUP - fonts, sizes, positions, paths
    fontTitle = ImageFont.truetype(config.FONTS["title"], config.FONT_SIZES["title"])
    fontSub = ImageFont.truetype(config.FONTS["subtitle"], config.FONT_SIZES["subtitle"])
    fontBody = ImageFont.truetype(config.FONTS["body"], config.FONT_SIZES["body"])
    valueSub = ImageFont.truetype(config.FONTS["subtitle"], config.FONT_SIZES["value"])
    fontAuthor = ImageFont.truetype(config.FONTS["subtitle"], config.FONT_SIZES["author"])
    cardWidth  = int(config.CARD_WIDTH_MM * config.DPI / 25.4)
    cardHeight = int(config.CARD_HEIGHT_MM * config.DPI / 25.4)
    titlePosition = (cardWidth // 2, int(0.12 * cardHeight))
    subtitlePosition = (cardWidth / 2, int(0.175 * cardHeight))
    valueSuitPosition = (int(0.11 * cardWidth), int(0.94 * cardHeight))
    authorPosition = (int(0.87 * cardWidth), int(0.92 * cardHeight))
    subtitleFlag = bool(subtitle)
    authorFlag = bool(author)

    if card_type in [0, 1, 2]:
        cardValueSuitFlag = True
        if subtitleFlag:
            art_x, art_y = int(0.17 * cardWidth), int(0.20 * cardHeight)
        else:
            art_x, art_y = int(0.17 * cardWidth), int(0.175 * cardHeight)
    else:
        cardValueSuitFlag = False
        if subtitleFlag:
            art_x, art_y = int(0.2 * cardWidth), int(0.20 * cardHeight)
        else:
            art_x, art_y = int(0.2 * cardWidth), int(0.175 * cardHeight)
    
    expArt_x, expArt_y = int(0.79 * cardWidth), int(0.021 * cardHeight)
    expansionArtSize = (int(0.15 * cardWidth), int(0.15 * cardWidth))
    artSize = (cardWidth - 2 * art_x, cardWidth - 2 * art_x)
    textStart_y= int(art_y + artSize[0] + 0.02 * cardHeight)
    textWidthPixels = cardWidth - (2 * art_x)

    ### 2. CREATE FACE CARD
    # Import template
    faceCard = Image.open(config.TEMPLATES[card_type]).convert("RGBA")
    faceCard = faceCard.resize((cardWidth, cardHeight), Image.LANCZOS)
    draw = ImageDraw.Draw(faceCard)

    # Add title
    draw.text(titlePosition, title, fill=config.TEXT_COLOR["title"], font=fontTitle, anchor="mm")

    # Add subtitle if provided
    if subtitleFlag:
        draw.text(subtitlePosition, subtitle.upper(), fill=config.TEXT_COLOR["subtitle"], font=fontSub, anchor="mm")

    # Add author if provided
    if authorFlag:
        draw.text(authorPosition, author.upper(), fill=config.TEXT_COLOR["author"], font=fontAuthor, anchor="rm")

    # Add artwork    
    artImg = Image.open(art).convert("RGBA")
    artImg = artImg.resize(artSize, Image.LANCZOS)

    # Add vignette (if enabled in config file)
    if config.VIGNETTE_FLAG:
        white_bg = Image.new("RGBA", artImg.size, config.VIGNETTE_COLOR)
        mask = Image.new("L", artImg.size, 255)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rectangle(
            [config.VIGNETTE_MARGIN, config.VIGNETTE_MARGIN, artSize[0] - config.VIGNETTE_MARGIN, artSize[1] - config.VIGNETTE_MARGIN],
            fill=0
        )
        mask = mask.filter(ImageFilter.GaussianBlur(radius=30))
        artImg = Image.composite(white_bg, artImg, mask)
    faceCard.paste(artImg, (int(art_x), int(art_y)), artImg)

    # Add expansion art if provided
    if expansionArt:
        expArtImg = Image.open(expansionArt).convert("RGBA")
        expArtImg = expArtImg.resize((expansionArtSize), Image.LANCZOS)
        faceCard.paste(expArtImg, (expArt_x, expArt_y), expArtImg)


    # Add card value and suit (if applicable)
    if cardValueSuitFlag:
        if cardValue == "Random":
            cardValue = random.choice(["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"])
        if cardValue == "10":
            modificator = 14
        else:
            modificator = 8

        # Paste suit image next to value
        suitImg = Image.open(config.SUITS[cardSuit]).convert("RGBA")
        suitImg = suitImg.resize((int(config.FONT_SIZES["value"]/1.3), int(config.FONT_SIZES["value"]/1.3)), Image.LANCZOS)
        faceCard.paste(suitImg, 
                       (int(valueSuitPosition[0] + fontSub.getlength(cardValue) / 2 + modificator), int(valueSuitPosition[1] - config.FONT_SIZES["value"] / 2)),
                       mask=suitImg
                       )

        # Draw outline for value text
        for adj_x in range(-config.VALUE_OUTLINE_WIDTH, config.VALUE_OUTLINE_WIDTH + 1):
            for adj_y in range(-config.VALUE_OUTLINE_WIDTH, config.VALUE_OUTLINE_WIDTH + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((valueSuitPosition[0] + adj_x, valueSuitPosition[1] + adj_y), 
                    cardValue.upper(), fill=(255, 255, 255, 255), font=valueSub, anchor="mm")

        # Add value text
        draw.text(valueSuitPosition, cardValue.upper(), fill=config.TEXT_COLOR["value"], font=valueSub, anchor="mm")
    
    ## Add border
    borderImg = Image.open(config.BORDER_PATH).convert("RGBA")
    borderImg = borderImg.resize((cardWidth, cardHeight), Image.LANCZOS)
    faceCard.paste(borderImg, (0,0), mask=borderImg)
    ## Add description text

    # Guess max chars per line based on average character width
    avgCharWidth = fontBody.getlength("x")
    max_chars = int(textWidthPixels / avgCharWidth)
    current_y = textStart_y
    lineHeight = fontBody.getbbox("Ay")[3] + 3
    
    # Add description with word wrapping
    paragraphs = description.splitlines()

    for para in paragraphs:
        if para.strip() == "":
            # Empty line → vertical spacing
            current_y += lineHeight
            continue

        wrapped_lines = textwrap.wrap(para, width=max_chars)

        for line in wrapped_lines:
            line_w = fontBody.getlength(line)
            line_x = (cardWidth - line_w) / 2
            draw.text((line_x, current_y), line, font=fontBody, fill=config.TEXT_COLOR["body"])
            current_y += lineHeight

    ### 3. CREATE BACK CARD (if requested)
    if backCardFlag:
        if cardValueSuitFlag:
            backCard = Image.open(config.BACK_PLAYING_PATH).convert("RGBA")
        else:
            backCard = Image.open(config.BACK_CHARACTER_PATH).convert("RGBA")
        backCard = backCard.resize((cardWidth, cardHeight), Image.LANCZOS)
        backCard.paste(borderImg, (0,0), mask=borderImg)
        
        combinedCard = Image.new("RGBA", (cardWidth * 2, cardHeight), (255, 255, 255, 255))
        combinedCard.paste(faceCard, (0, 0), mask=faceCard)
        combinedCard.paste(backCard, (cardWidth, 0), mask=backCard)
    else:
        combinedCard = Image.new("RGBA", (cardWidth, cardHeight), (255, 255, 255, 255))
        combinedCard.paste(faceCard, (0, 0), mask=faceCard)

    ### 4. RETURN RESULT
    # Convert RGBA to RGB for PhotoImage compatibility
    if combinedCard.mode == 'RGBA':
        combinedCard = combinedCard.convert('RGB')
    photoimage = ImageTk.PhotoImage(combinedCard)
    return combinedCard if return_pil else photoimage

# ---------- GUI logic ----------
def choose_file(selectedPath):
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[
            ("All supported files", "*.png *.jpg"),
            ("PNG files", "*.png"),
            ("JPG files", "*.jpg"),
            ("All files", "*.*")
        ]
    )
    if file_path:
        selectedPath.set(file_path)
        print("Selected file:", file_path)

def update_image():
    cardType = cardTypeGUI.get()
    art = selectedArtPath.get()
    expansionArt = selectedExpansionArtPath.get()
    cardValue = cardValueGUI.get()
    cardSuit = cardSuitGUI.get()
    title = titleGUI.get()
    subtitle = subtitleGUI.get()
    author = authorGUI.get()
    description = descripGUI.get("1.0", "end-1c")
    backCardFlag = backCardFlagGUI.get()

    pil_img = generate_card(
        cardType, art, cardValue, cardSuit,
        title, subtitle, author, description,
        backCardFlag, expansionArt,
        return_pil=True
    )

    # Scale for screen preview
    scale = 0.5
    preview_size = (
        int(pil_img.width * scale),
        int(pil_img.height * scale)
    )

    preview_img = pil_img.resize(preview_size, Image.LANCZOS)

    tk_img = ImageTk.PhotoImage(preview_img)
    image.config(image=tk_img)
    image.image = tk_img

def save_image():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg"), ("All files", "*.*")]
    )
    cardType = cardTypeGUI.get()
    art = selectedArtPath.get()
    expansionArt = selectedExpansionArtPath.get()
    cardValue = cardValueGUI.get()
    cardSuit = cardSuitGUI.get()
    title = titleGUI.get()
    subtitle = subtitleGUI.get()
    author = authorGUI.get()
    description = descripGUI.get("1.0", "end-1c")
    backCardFlag = backCardFlagGUI.get()
    # Reconstruct and save the card
    card = generate_card(cardType, art, cardValue, cardSuit, title, subtitle, author, description, backCardFlag, expansionArt, return_pil=True)
    # Save the PIL Image
    card.save(file_path, dpi=(config.DPI, config.DPI))

def toggle_value_suit_visibility():
    if cardTypeGUI.get() in [0, 1, 2]:
        card_value.config(state="readonly")
        for child in suits_frame.winfo_children():
            child.config(state="normal")
    else:
        card_value.config(state="disabled")
        for child in suits_frame.winfo_children():
            child.config(state="disabled")


# ---------- GUI ----------
root = tk.Tk()
root.title("Bang! Card Generator")
root.resizable(False, False)
# Create menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)

# Help menu
help_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Open README", command=lambda: __import__('webbrowser').open(config.README_PATH.as_uri()))

# Config menu
config_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Config", menu=config_menu)
config_menu.add_command(label="Edit config.py", command=lambda: __import__('subprocess').Popen(["notepad", './config.py']) if __import__('sys').platform == 'win32' else __import__('subprocess').Popen(['gedit', './config.py']))
config_menu.add_command(label="Reload Config", command=lambda: __import__('importlib').reload(config) and update_image())

# Upper frame for settings
upper_frame = tk.Frame(root, width = config.SCREEN_SIZE[0])  # fixed width
upper_frame.pack(side=tk.TOP, fill=tk.Y, padx=10, pady=10)  # only fill vertically

canvas = Canvas(root, width=config.SCREEN_SIZE[0],height=2)
canvas.pack()
canvas.pack_propagate(False)
canvas.create_line(0, 2, config.SCREEN_SIZE[0], 2)

control_buttons_frame = tk.Frame(root, width = config.SCREEN_SIZE[0], height=50) 
control_buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

canvas = Canvas(root, width=config.SCREEN_SIZE[0],height=2)
canvas.pack_propagate(False)
canvas.pack()
canvas.create_line(0, 2, config.SCREEN_SIZE[0], 2)

# Right frame for image
lower_frame = tk.Frame(root, width = config.SCREEN_SIZE[0])  # fixed width
lower_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)  # only fill vertically

cardtype_frame = tk.Frame(upper_frame)
cardtype_frame.pack(side=tk.LEFT, padx=10, anchor="n")
art_frame = tk.Frame(upper_frame)
art_frame.pack(side=tk.LEFT, padx=10, anchor="n")

# Card type
card_type_label = tk.Label(cardtype_frame, text="Choose card type:")
card_type_label.pack(anchor=tk.W, pady=(10, 0))
cardTypeGUI = tk.IntVar(value=0)  # Initialize with a default value
tk.Radiobutton(cardtype_frame, text="Action Card", variable=cardTypeGUI, value=0).pack(anchor=tk.W)
tk.Radiobutton(cardtype_frame, text="Blue Item Card", variable=cardTypeGUI, value=1).pack(anchor=tk.W)
tk.Radiobutton(cardtype_frame, text="Green Item Card", variable=cardTypeGUI, value=2).pack(anchor=tk.W)
tk.Radiobutton(cardtype_frame, text="Character Card - 3 lives", variable=cardTypeGUI, value=3).pack(anchor=tk.W)
tk.Radiobutton(cardtype_frame, text="Character Card - 4 lives", variable=cardTypeGUI, value=4).pack(anchor=tk.W)
tk.Radiobutton(cardtype_frame, text="Character Card - 5 lives", variable=cardTypeGUI, value=5).pack(anchor=tk.W)
tk.Radiobutton(cardtype_frame, text="Character Card - 6 lives", variable=cardTypeGUI, value=6).pack(anchor=tk.W)

# Add art
art_label = tk.Label(art_frame, text="Choose artwork:")
art_label.pack(anchor=tk.W, pady=(10, 0))
artGUI_label = tk.Label(art_frame, text="Upload artwork file (.png, .jpg):")
artGUI_label.pack(anchor=tk.W, pady=(10, 0))
selectedArtPath = tk.StringVar(value=config.DEFAULT_ART_PATH)
artGUI = tk.Button(art_frame, text="Import Artwork", command=lambda: choose_file(selectedArtPath))
artGUI.pack(pady=10)
artGUI_path_label = tk.Label(art_frame, textvariable=selectedArtPath, wraplength=280, justify="left")
artGUI_path_label.pack(anchor=tk.W, pady=5)

# Add expansion art
expansionArtGUI_label = tk.Label(art_frame, text="Upload expansion art file (.png, .jpg) (optional):")
expansionArtGUI_label.pack(anchor=tk.W, pady=(10, 0))
selectedExpansionArtPath = tk.StringVar(value="")
expansionArtGUI = tk.Button(art_frame, text="Import Expansion Artwork", command=lambda: choose_file(selectedExpansionArtPath))
expansionArtGUI.pack(pady=10)
expansionArtGUI_path_label = tk.Label(art_frame, textvariable=selectedExpansionArtPath, wraplength=280, justify="left")
expansionArtGUI_path_label.pack(anchor=tk.W, pady=5)

# Choose value/suit flag
value_suit_label = tk.Label(cardtype_frame, text="Card Value/Suit:")
value_suit_label.pack(anchor=tk.W, pady=(5, 0))
cardValueGUI = tk.StringVar(value="Random")
card_value = ttk.Combobox(
    cardtype_frame,
    values=["Random","2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"],
    textvariable=cardValueGUI,
    state="readonly"
)
card_value.pack(anchor=tk.W, pady=5)
card_value.set("Random")

suits = {
    'hearts': tk.PhotoImage(file=config.SUITS[0]).subsample(6, 6),
    'clubs': tk.PhotoImage(file=config.SUITS[1]).subsample(6, 6),
    'diamonds': tk.PhotoImage(file=config.SUITS[2]).subsample(6, 6),
    'spades': tk.PhotoImage(file=config.SUITS[3]).subsample(6, 6)
}
suits_frame = tk.Frame(cardtype_frame)
suits_frame.pack(anchor=tk.W, pady=5)
cardSuitGUI = tk.IntVar(value=0)
tk.Radiobutton(suits_frame, image=suits["hearts"], variable=cardSuitGUI, value=0).pack(side=tk.LEFT)
tk.Radiobutton(suits_frame, image=suits["clubs"], variable=cardSuitGUI, value=1).pack(side=tk.LEFT, padx=2)
tk.Radiobutton(suits_frame, image=suits["diamonds"], variable=cardSuitGUI, value=2).pack(side=tk.LEFT, padx=2)
tk.Radiobutton(suits_frame, image=suits["spades"], variable=cardSuitGUI, value=3).pack(side=tk.LEFT, padx=2)

# Title input
titleGUI_label = tk.Label(upper_frame, text="Card Title:")
titleGUI_label.pack(anchor=tk.W, pady=(10, 0))
titleGUI = tk.Entry(upper_frame, width=30)
titleGUI.insert(0, "Bang")
titleGUI.pack(anchor=tk.W)


# Subtitle input
subtitleGUI_label = tk.Label(upper_frame, text="Subtitle (Optional):")
subtitleGUI_label.pack(anchor=tk.W, pady=(10, 0))
subtitleGUI = tk.Entry(upper_frame, width=30)
subtitleGUI.insert(0, "Subtitle")
subtitleGUI.pack(anchor=tk.W)

# Author input
authorGUI_label = tk.Label(upper_frame, text="Author (Optional):")
authorGUI_label.pack(anchor=tk.W, pady=(10, 0))
authorGUI = tk.Entry(upper_frame, width=30)
authorGUI.insert(0, "Author")
authorGUI.pack(anchor=tk.W)

# Description input
descripGUI_label = tk.Label(upper_frame, text="Description:")
descripGUI_label.pack(anchor=tk.W, pady=(10, 0))
descripGUI = tk.Text(upper_frame, width=30, height=8, wrap="word")
descripGUI.insert("1.0", "Description text goes here.")
descripGUI.pack(anchor=tk.W)

# Prompt for back card
backGUI_label = tk.Label(upper_frame, text="Do you wish to create card back?")
backGUI_label.pack(side=tk.LEFT, pady=(0, 0))
backCardFlagGUI = tk.BooleanVar(value=True)
back_frame = tk.Frame(upper_frame)
back_frame.pack(anchor=tk.W, pady=5)
tk.Radiobutton(back_frame, text="Y", variable=backCardFlagGUI, value=True).pack(side=tk.LEFT)
tk.Radiobutton(back_frame, text="N", variable=backCardFlagGUI, value=False).pack(side=tk.LEFT, padx=2)

# Image display
image_label = tk.Label(lower_frame, text="Card Preview:")
image_label.pack(pady=(10, 0))
image = tk.Label(lower_frame, text="Card Preview")
image.pack()

# Save button
save_button = tk.Button(control_buttons_frame, text="Export Card as..", command=save_image, width=20, height=2)
save_button.pack(pady=10)
# Initial render
update_image()

# Bind events to update image automatically
titleGUI.bind("<KeyRelease>", lambda e: update_image())
subtitleGUI.bind("<KeyRelease>", lambda e: update_image())
authorGUI.bind("<KeyRelease>", lambda e: update_image())
descripGUI.bind("<KeyRelease>", lambda e: update_image())
card_value.bind("<<ComboboxSelected>>", lambda e: update_image())
cardSuitGUI.trace_add("write", lambda *args: update_image())
cardTypeGUI.trace_add("write", lambda *args: update_image())
cardTypeGUI.trace_add("write", lambda *args: toggle_value_suit_visibility())
backCardFlagGUI.trace_add("write", lambda *args: update_image())
selectedArtPath.trace_add("write", lambda *args: update_image())
selectedExpansionArtPath.trace_add("write", lambda *args: update_image())

root.mainloop()
