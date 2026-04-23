import json
import random
import textwrap
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk, Canvas
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageTk,
)

import config

CARDS_FILE = Path(__file__).parent / "cards.json"


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

    # Guess max chars per line based on average character width
    avgCharWidth = fontBody.getlength("x")
    max_chars = int(textWidthPixels / avgCharWidth)
    current_y = textStart_y
    lineHeight = fontBody.getbbox("Ay")[3] + 3

    # Add description with word wrapping
    paragraphs = description.splitlines()

    for para in paragraphs:
        if para.strip() == "":
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
    if combinedCard.mode == 'RGBA':
        combinedCard = combinedCard.convert('RGB')
    photoimage = ImageTk.PhotoImage(combinedCard)
    return combinedCard if return_pil else photoimage


# ---------- App class ----------
class BangCardGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bang! Card Generator")
        self.root.resizable(False, False)
        self.cards = []
        self.current_card_index = None
        self._loading = False
        self._load_cards_from_file()
        self._build_ui()
        if self.cards:
            self._select_card(0)
        else:
            self._add_card()

    # ── persistence ───────────────────────────────────────────────────────────

    def _load_cards_from_file(self):
        if CARDS_FILE.exists():
            with open(CARDS_FILE, "r", encoding="utf-8") as f:
                self.cards = json.load(f)

    def _save_cards_to_file(self):
        with open(CARDS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.cards, f, ensure_ascii=False, indent=2)

    # ── form <-> data ─────────────────────────────────────────────────────────

    def _collect_form_data(self):
        return {
            "card_type": self.cardTypeGUI.get(),
            "card_value": self.cardValueGUI.get(),
            "card_suit": self.cardSuitGUI.get(),
            "title": self.titleGUI.get(),
            "subtitle": self.subtitleGUI.get(),
            "author": self.authorGUI.get(),
            "description": self.descripGUI.get("1.0", "end-1c"),
            "back_card": self.backCardFlagGUI.get(),
            "art_path": self.selectedArtPath.get(),
            "expansion_art_path": self.selectedExpansionArtPath.get(),
        }

    def _fill_form(self, data):
        self._loading = True
        self.cardTypeGUI.set(data.get("card_type", 0))
        self.cardValueGUI.set(data.get("card_value", "Random"))
        self.cardSuitGUI.set(data.get("card_suit", 0))
        self.titleGUI.delete(0, tk.END)
        self.titleGUI.insert(0, data.get("title", ""))
        self.subtitleGUI.delete(0, tk.END)
        self.subtitleGUI.insert(0, data.get("subtitle", ""))
        self.authorGUI.delete(0, tk.END)
        self.authorGUI.insert(0, data.get("author", ""))
        self.descripGUI.delete("1.0", tk.END)
        self.descripGUI.insert("1.0", data.get("description", ""))
        self.backCardFlagGUI.set(data.get("back_card", True))
        self.selectedArtPath.set(data.get("art_path", str(config.DEFAULT_ART_PATH)))
        self.selectedExpansionArtPath.set(data.get("expansion_art_path", ""))
        self._loading = False
        self.toggle_value_suit_visibility()
        self.update_image()

    # ── card list management ──────────────────────────────────────────────────

    def _refresh_listbox(self):
        self.cards_listbox.delete(0, tk.END)
        for card in self.cards:
            self.cards_listbox.insert(tk.END, card.get("title") or "Untitled")
        if self.current_card_index is not None:
            self.cards_listbox.selection_set(self.current_card_index)
            self.cards_listbox.see(self.current_card_index)

    def _add_card(self):
        new_card = {
            "card_type": 0,
            "card_value": "Random",
            "card_suit": 0,
            "title": "New Card",
            "subtitle": "",
            "author": "",
            "description": "",
            "back_card": True,
            "art_path": str(config.DEFAULT_ART_PATH),
            "expansion_art_path": "",
        }
        self.cards.append(new_card)
        self.current_card_index = len(self.cards) - 1
        self._refresh_listbox()
        self._fill_form(new_card)
        self._save_cards_to_file()

    def _delete_card(self):
        if self.current_card_index is None:
            return
        self.cards.pop(self.current_card_index)
        if not self.cards:
            self.current_card_index = None
            self._add_card()
            return
        self.current_card_index = min(self.current_card_index, len(self.cards) - 1)
        self._refresh_listbox()
        self._fill_form(self.cards[self.current_card_index])
        self._save_cards_to_file()

    def _select_card(self, index):
        self.current_card_index = index
        self.cards_listbox.selection_clear(0, tk.END)
        self.cards_listbox.selection_set(index)
        self.cards_listbox.see(index)
        self._fill_form(self.cards[index])

    def _on_card_select(self, event):
        selection = self.cards_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index == self.current_card_index:
            return
        self._select_card(index)

    def _autosave(self):
        if self._loading or self.current_card_index is None:
            return
        data = self._collect_form_data()
        self.cards[self.current_card_index] = data
        self.cards_listbox.delete(self.current_card_index)
        self.cards_listbox.insert(self.current_card_index, data.get("title") or "Untitled")
        self.cards_listbox.selection_set(self.current_card_index)
        self._save_cards_to_file()

    def _on_field_change(self):
        self._autosave()
        self.update_image()

    def _on_card_type_change(self):
        self.toggle_value_suit_visibility()
        self._on_field_change()

    # ── UI building ───────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_menu()

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        sidebar_frame = tk.Frame(main_frame, width=180, relief=tk.RIDGE, bd=1)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        sidebar_frame.pack_propagate(False)
        self._build_sidebar(sidebar_frame)

        content_frame = tk.Frame(main_frame)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        self._build_content(content_frame)

    def _build_sidebar(self, parent):
        tk.Label(parent, text="Cards", font=("", 10, "bold")).pack(pady=(8, 4))

        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.cards_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            activestyle="none",
        )
        scrollbar.config(command=self.cards_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cards_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.cards_listbox.bind("<<ListboxSelect>>", self._on_card_select)

        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(btn_frame, text="+ New", command=self._add_card, width=7).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Delete", command=self._delete_card, width=7).pack(side=tk.RIGHT)

    def _build_content(self, parent):
        upper_frame = tk.Frame(parent, width=config.SCREEN_SIZE[0])
        upper_frame.pack(side=tk.TOP, fill=tk.Y, padx=10, pady=10)

        canvas = Canvas(parent, width=config.SCREEN_SIZE[0], height=2)
        canvas.pack()
        canvas.pack_propagate(False)
        canvas.create_line(0, 2, config.SCREEN_SIZE[0], 2)

        control_buttons_frame = tk.Frame(parent, width=config.SCREEN_SIZE[0], height=50)
        control_buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        canvas2 = Canvas(parent, width=config.SCREEN_SIZE[0], height=2)
        canvas2.pack_propagate(False)
        canvas2.pack()
        canvas2.create_line(0, 2, config.SCREEN_SIZE[0], 2)

        lower_frame = tk.Frame(parent, width=config.SCREEN_SIZE[0])
        lower_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        cardtype_frame = tk.Frame(upper_frame)
        cardtype_frame.pack(side=tk.LEFT, padx=10, anchor="n")
        art_frame = tk.Frame(upper_frame)
        art_frame.pack(side=tk.LEFT, padx=10, anchor="n")

        # Card type
        tk.Label(cardtype_frame, text="Choose card type:").pack(anchor=tk.W, pady=(10, 0))
        self.cardTypeGUI = tk.IntVar(value=0)
        tk.Radiobutton(cardtype_frame, text="Action Card",              variable=self.cardTypeGUI, value=0).pack(anchor=tk.W)
        tk.Radiobutton(cardtype_frame, text="Blue Item Card",           variable=self.cardTypeGUI, value=1).pack(anchor=tk.W)
        tk.Radiobutton(cardtype_frame, text="Green Item Card",          variable=self.cardTypeGUI, value=2).pack(anchor=tk.W)
        tk.Radiobutton(cardtype_frame, text="Character Card - 3 lives", variable=self.cardTypeGUI, value=3).pack(anchor=tk.W)
        tk.Radiobutton(cardtype_frame, text="Character Card - 4 lives", variable=self.cardTypeGUI, value=4).pack(anchor=tk.W)
        tk.Radiobutton(cardtype_frame, text="Character Card - 5 lives", variable=self.cardTypeGUI, value=5).pack(anchor=tk.W)
        tk.Radiobutton(cardtype_frame, text="Character Card - 6 lives", variable=self.cardTypeGUI, value=6).pack(anchor=tk.W)

        # Artwork
        tk.Label(art_frame, text="Choose artwork:").pack(anchor=tk.W, pady=(10, 0))
        tk.Label(art_frame, text="Upload artwork file (.png, .jpg):").pack(anchor=tk.W, pady=(10, 0))
        self.selectedArtPath = tk.StringVar(value=str(config.DEFAULT_ART_PATH))
        tk.Button(art_frame, text="Import Artwork", command=lambda: self.choose_file(self.selectedArtPath)).pack(pady=10)
        tk.Label(art_frame, textvariable=self.selectedArtPath, wraplength=280, justify="left").pack(anchor=tk.W, pady=5)

        # Expansion artwork
        tk.Label(art_frame, text="Upload expansion art file (.png, .jpg) (optional):").pack(anchor=tk.W, pady=(10, 0))
        self.selectedExpansionArtPath = tk.StringVar(value="")
        tk.Button(art_frame, text="Import Expansion Artwork", command=lambda: self.choose_file(self.selectedExpansionArtPath)).pack(pady=10)
        tk.Label(art_frame, textvariable=self.selectedExpansionArtPath, wraplength=280, justify="left").pack(anchor=tk.W, pady=5)

        # Card value / suit
        tk.Label(cardtype_frame, text="Card Value/Suit:").pack(anchor=tk.W, pady=(5, 0))
        self.cardValueGUI = tk.StringVar(value="Random")
        self.card_value = ttk.Combobox(
            cardtype_frame,
            values=["Random", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"],
            textvariable=self.cardValueGUI,
            state="readonly",
        )
        self.card_value.pack(anchor=tk.W, pady=5)
        self.card_value.set("Random")

        suits = {
            'hearts':   tk.PhotoImage(file=config.SUITS[0]).subsample(6, 6),
            'clubs':    tk.PhotoImage(file=config.SUITS[1]).subsample(6, 6),
            'diamonds': tk.PhotoImage(file=config.SUITS[2]).subsample(6, 6),
            'spades':   tk.PhotoImage(file=config.SUITS[3]).subsample(6, 6),
        }
        self.suits_frame = tk.Frame(cardtype_frame)
        self.suits_frame.pack(anchor=tk.W, pady=5)
        self.cardSuitGUI = tk.IntVar(value=0)
        tk.Radiobutton(self.suits_frame, image=suits["hearts"],   variable=self.cardSuitGUI, value=0).pack(side=tk.LEFT)
        tk.Radiobutton(self.suits_frame, image=suits["clubs"],    variable=self.cardSuitGUI, value=1).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(self.suits_frame, image=suits["diamonds"], variable=self.cardSuitGUI, value=2).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(self.suits_frame, image=suits["spades"],   variable=self.cardSuitGUI, value=3).pack(side=tk.LEFT, padx=2)
        self.suits_frame._suit_images = suits

        # Title
        tk.Label(upper_frame, text="Card Title:").pack(anchor=tk.W, pady=(10, 0))
        self.titleGUI = tk.Entry(upper_frame, width=30)
        self.titleGUI.pack(anchor=tk.W)

        # Subtitle
        tk.Label(upper_frame, text="Subtitle (Optional):").pack(anchor=tk.W, pady=(10, 0))
        self.subtitleGUI = tk.Entry(upper_frame, width=30)
        self.subtitleGUI.pack(anchor=tk.W)

        # Author
        tk.Label(upper_frame, text="Author (Optional):").pack(anchor=tk.W, pady=(10, 0))
        self.authorGUI = tk.Entry(upper_frame, width=30)
        self.authorGUI.pack(anchor=tk.W)

        # Description
        tk.Label(upper_frame, text="Description:").pack(anchor=tk.W, pady=(10, 0))
        self.descripGUI = tk.Text(upper_frame, width=30, height=8, wrap="word")
        self.descripGUI.pack(anchor=tk.W)

        # Card back
        tk.Label(upper_frame, text="Do you wish to create card back?").pack(side=tk.LEFT, pady=(0, 0))
        self.backCardFlagGUI = tk.BooleanVar(value=True)
        back_frame = tk.Frame(upper_frame)
        back_frame.pack(anchor=tk.W, pady=5)
        tk.Radiobutton(back_frame, text="Y", variable=self.backCardFlagGUI, value=True).pack(side=tk.LEFT)
        tk.Radiobutton(back_frame, text="N", variable=self.backCardFlagGUI, value=False).pack(side=tk.LEFT, padx=2)

        # Preview
        tk.Label(lower_frame, text="Card Preview:").pack(pady=(10, 0))
        self.image_label = tk.Label(lower_frame, text="Card Preview")
        self.image_label.pack()

        # Export button
        tk.Button(control_buttons_frame, text="Export Card as..", command=self.save_image, width=20, height=2).pack(pady=10)

        # Bindings
        self.titleGUI.bind("<KeyRelease>", lambda e: self._on_field_change())
        self.subtitleGUI.bind("<KeyRelease>", lambda e: self._on_field_change())
        self.authorGUI.bind("<KeyRelease>", lambda e: self._on_field_change())
        self.descripGUI.bind("<KeyRelease>", lambda e: self._on_field_change())
        self.card_value.bind("<<ComboboxSelected>>", lambda e: self._on_field_change())
        self.cardSuitGUI.trace_add("write", lambda *args: self._on_field_change())
        self.cardTypeGUI.trace_add("write", lambda *args: self._on_card_type_change())
        self.backCardFlagGUI.trace_add("write", lambda *args: self._on_field_change())
        self.selectedArtPath.trace_add("write", lambda *args: self._on_field_change())
        self.selectedExpansionArtPath.trace_add("write", lambda *args: self._on_field_change())

    def _build_menu(self):
        import webbrowser
        import subprocess
        import sys
        import importlib

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Open README", command=lambda: webbrowser.open(config.README_PATH.as_uri()))

        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Config", menu=config_menu)
        if sys.platform == "win32":
            config_menu.add_command(label="Edit config.py", command=lambda: subprocess.Popen(["notepad", str(config.CONFIG_PATH)]))
        else:
            config_menu.add_command(label="Edit config.py", command=lambda: subprocess.Popen(["gedit", str(config.CONFIG_PATH)]))
        config_menu.add_command(label="Reload Config", command=lambda: importlib.reload(config) or self.update_image())

    def choose_file(self, selected_path):
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[
                ("All supported files", "*.png *.jpg"),
                ("PNG files", "*.png"),
                ("JPG files", "*.jpg"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            selected_path.set(file_path)

    def update_image(self):
        pil_img = generate_card(
            self.cardTypeGUI.get(),
            self.selectedArtPath.get(),
            self.cardValueGUI.get(),
            self.cardSuitGUI.get(),
            self.titleGUI.get(),
            self.subtitleGUI.get(),
            self.authorGUI.get(),
            self.descripGUI.get("1.0", "end-1c"),
            self.backCardFlagGUI.get(),
            self.selectedExpansionArtPath.get(),
            return_pil=True,
        )

        scale = 0.5
        preview_size = (int(pil_img.width * scale), int(pil_img.height * scale))
        preview_img = pil_img.resize(preview_size, Image.LANCZOS)

        tk_img = ImageTk.PhotoImage(preview_img)
        self.image_label.config(image=tk_img)
        self.image_label.image = tk_img

    def save_image(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg"), ("All files", "*.*")],
        )
        if not file_path:
            return
        card = generate_card(
            self.cardTypeGUI.get(),
            self.selectedArtPath.get(),
            self.cardValueGUI.get(),
            self.cardSuitGUI.get(),
            self.titleGUI.get(),
            self.subtitleGUI.get(),
            self.authorGUI.get(),
            self.descripGUI.get("1.0", "end-1c"),
            self.backCardFlagGUI.get(),
            self.selectedExpansionArtPath.get(),
            return_pil=True,
        )
        card.save(file_path, dpi=(config.DPI, config.DPI))

    def toggle_value_suit_visibility(self):
        if self.cardTypeGUI.get() in [0, 1, 2]:
            self.card_value.config(state="readonly")
            for child in self.suits_frame.winfo_children():
                child.config(state="normal")
        else:
            self.card_value.config(state="disabled")
            for child in self.suits_frame.winfo_children():
                child.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    BangCardGeneratorApp(root)
    root.mainloop()
