import json
import random
import textwrap
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageTk,
)

import config

CARDS_FILE = Path(__file__).parent / "cards.json"

# ── Sidebar palette ───────────────────────────────────────────────────────────
_SB_BG      = "#2D3748"
_SB_LIST_BG = "#1E293B"
_SB_FG      = "#F8FAFC"
_SB_SEL_BG  = "#3B82F6"


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
    faceCard = Image.open(config.TEMPLATES[card_type]).convert("RGBA")
    faceCard = faceCard.resize((cardWidth, cardHeight), Image.LANCZOS)
    draw = ImageDraw.Draw(faceCard)

    draw.text(titlePosition, title, fill=config.TEXT_COLOR["title"], font=fontTitle, anchor="mm")

    if subtitleFlag:
        draw.text(subtitlePosition, subtitle.upper(), fill=config.TEXT_COLOR["subtitle"], font=fontSub, anchor="mm")

    if authorFlag:
        draw.text(authorPosition, author.upper(), fill=config.TEXT_COLOR["author"], font=fontAuthor, anchor="rm")

    artImg = Image.open(art).convert("RGBA")
    artImg = artImg.resize(artSize, Image.LANCZOS)

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

    if expansionArt:
        expArtImg = Image.open(expansionArt).convert("RGBA")
        expArtImg = expArtImg.resize((expansionArtSize), Image.LANCZOS)
        faceCard.paste(expArtImg, (expArt_x, expArt_y), expArtImg)

    if cardValueSuitFlag:
        if cardValue == "Random":
            cardValue = random.choice(["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"])
        if cardValue == "10":
            modificator = 14
        else:
            modificator = 8

        suitImg = Image.open(config.SUITS[cardSuit]).convert("RGBA")
        suitImg = suitImg.resize((int(config.FONT_SIZES["value"]/1.3), int(config.FONT_SIZES["value"]/1.3)), Image.LANCZOS)
        faceCard.paste(suitImg,
                       (int(valueSuitPosition[0] + fontSub.getlength(cardValue) / 2 + modificator), int(valueSuitPosition[1] - config.FONT_SIZES["value"] / 2)),
                       mask=suitImg)

        for adj_x in range(-config.VALUE_OUTLINE_WIDTH, config.VALUE_OUTLINE_WIDTH + 1):
            for adj_y in range(-config.VALUE_OUTLINE_WIDTH, config.VALUE_OUTLINE_WIDTH + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((valueSuitPosition[0] + adj_x, valueSuitPosition[1] + adj_y),
                              cardValue.upper(), fill=(255, 255, 255, 255), font=valueSub, anchor="mm")

        draw.text(valueSuitPosition, cardValue.upper(), fill=config.TEXT_COLOR["value"], font=valueSub, anchor="mm")

    borderImg = Image.open(config.BORDER_PATH).convert("RGBA")
    borderImg = borderImg.resize((cardWidth, cardHeight), Image.LANCZOS)
    faceCard.paste(borderImg, (0, 0), mask=borderImg)

    avgCharWidth = fontBody.getlength("x")
    max_chars = int(textWidthPixels / avgCharWidth)
    current_y = textStart_y
    lineHeight = fontBody.getbbox("Ay")[3] + 3

    for para in description.splitlines():
        if para.strip() == "":
            current_y += lineHeight
            continue
        for line in textwrap.wrap(para, width=max_chars):
            line_w = fontBody.getlength(line)
            line_x = (cardWidth - line_w) / 2
            draw.text((line_x, current_y), line, font=fontBody, fill=config.TEXT_COLOR["body"])
            current_y += lineHeight

    ### 3. CREATE BACK CARD (if requested)
    if backCardFlag:
        backCard = Image.open(config.BACK_PLAYING_PATH if cardValueSuitFlag else config.BACK_CHARACTER_PATH).convert("RGBA")
        backCard = backCard.resize((cardWidth, cardHeight), Image.LANCZOS)
        backCard.paste(borderImg, (0, 0), mask=borderImg)
        combinedCard = Image.new("RGBA", (cardWidth * 2, cardHeight), (255, 255, 255, 255))
        combinedCard.paste(faceCard, (0, 0), mask=faceCard)
        combinedCard.paste(backCard, (cardWidth, 0), mask=backCard)
    else:
        combinedCard = Image.new("RGBA", (cardWidth, cardHeight), (255, 255, 255, 255))
        combinedCard.paste(faceCard, (0, 0), mask=faceCard)

    if combinedCard.mode == "RGBA":
        combinedCard = combinedCard.convert("RGB")
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
        self._setup_style()
        self._build_ui()
        if self.cards:
            self._select_card(0)
        else:
            self._add_card()

    # ── style ─────────────────────────────────────────────────────────────────

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton", padding=(10, 6), font=("Helvetica", 10))

        style.configure("Primary.TButton",
                        background="#2563EB", foreground="white",
                        font=("Helvetica", 10, "bold"), padding=(14, 7))
        style.map("Primary.TButton",
                  background=[("active", "#1D4ED8"), ("disabled", "#93C5FD")])

        style.configure("Success.TButton",
                        background="#16A34A", foreground="white",
                        font=("Helvetica", 10, "bold"), padding=(14, 7))
        style.map("Success.TButton",
                  background=[("active", "#15803D"), ("disabled", "#86EFAC")])

        style.configure("Danger.TButton",
                        background="#DC2626", foreground="white", padding=(8, 5))
        style.map("Danger.TButton",
                  background=[("active", "#B91C1C")])

        style.configure("TLabelframe.Label", font=("Helvetica", 10, "bold"))
        style.configure("TLabelframe", padding=8)
        style.configure("Sidebar.TButton", padding=(6, 4))

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

        sidebar_frame = tk.Frame(main_frame, width=190, bg=_SB_BG)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_frame.pack_propagate(False)
        self._build_sidebar(sidebar_frame)

        content_frame = tk.Frame(main_frame)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        self._build_content(content_frame)

    def _build_sidebar(self, parent):
        tk.Label(parent, text="CARDS", font=("Helvetica", 11, "bold"),
                 bg=_SB_BG, fg=_SB_FG).pack(pady=(14, 6), padx=8, anchor=tk.W)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=8, pady=(0, 6))

        list_frame = tk.Frame(parent, bg=_SB_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.cards_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            activestyle="none",
            bg=_SB_LIST_BG,
            fg=_SB_FG,
            selectbackground=_SB_SEL_BG,
            selectforeground="white",
            font=("Helvetica", 10),
            bd=0,
            highlightthickness=0,
            relief=tk.FLAT,
        )
        scrollbar.config(command=self.cards_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cards_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.cards_listbox.bind("<<ListboxSelect>>", self._on_card_select)

        btn_frame = tk.Frame(parent, bg=_SB_BG)
        btn_frame.pack(fill=tk.X, padx=8, pady=10)
        ttk.Button(btn_frame, text="+ New", command=self._add_card).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(btn_frame, text="Delete", command=self._delete_card, style="Danger.TButton").pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _build_content(self, parent):
        # ── Two-column settings area ───────────────────────────────────────
        settings_frame = tk.Frame(parent)
        settings_frame.pack(side=tk.TOP, fill=tk.X, padx=14, pady=(12, 4))

        left_col = tk.Frame(settings_frame)
        left_col.pack(side=tk.LEFT, fill=tk.Y, anchor="n", padx=(0, 10))

        right_col = tk.Frame(settings_frame)
        right_col.pack(side=tk.LEFT, fill=tk.Y, anchor="n")

        # ── Card Type ─────────────────────────────────────────────────────
        type_lf = ttk.LabelFrame(left_col, text="Card Type")
        type_lf.pack(fill=tk.X, pady=(0, 8))

        self.cardTypeGUI = tk.IntVar(value=0)
        for value, label in [
            (0, "Action Card"),
            (1, "Blue Item Card"),
            (2, "Green Item Card"),
            (3, "Character Card – 3 lives"),
            (4, "Character Card – 4 lives"),
            (5, "Character Card – 5 lives"),
            (6, "Character Card – 6 lives"),
        ]:
            ttk.Radiobutton(type_lf, text=label, variable=self.cardTypeGUI, value=value).pack(anchor=tk.W)

        ttk.Separator(type_lf, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(8, 6))

        ttk.Label(type_lf, text="Value / Suit").pack(anchor=tk.W)
        self.cardValueGUI = tk.StringVar(value="Random")
        self.card_value = ttk.Combobox(
            type_lf,
            values=["Random", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"],
            textvariable=self.cardValueGUI,
            state="readonly",
            width=10,
        )
        self.card_value.pack(anchor=tk.W, pady=(2, 6))

        suits = {
            "hearts":   tk.PhotoImage(file=config.SUITS[0]).subsample(6, 6),
            "clubs":    tk.PhotoImage(file=config.SUITS[1]).subsample(6, 6),
            "diamonds": tk.PhotoImage(file=config.SUITS[2]).subsample(6, 6),
            "spades":   tk.PhotoImage(file=config.SUITS[3]).subsample(6, 6),
        }
        self.suits_frame = tk.Frame(type_lf)
        self.suits_frame.pack(anchor=tk.W, pady=(0, 4))
        self.cardSuitGUI = tk.IntVar(value=0)
        tk.Radiobutton(self.suits_frame, image=suits["hearts"],   variable=self.cardSuitGUI, value=0).pack(side=tk.LEFT)
        tk.Radiobutton(self.suits_frame, image=suits["clubs"],    variable=self.cardSuitGUI, value=1).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(self.suits_frame, image=suits["diamonds"], variable=self.cardSuitGUI, value=2).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(self.suits_frame, image=suits["spades"],   variable=self.cardSuitGUI, value=3).pack(side=tk.LEFT, padx=2)
        self.suits_frame._suit_images = suits

        # ── Artwork ───────────────────────────────────────────────────────
        art_lf = ttk.LabelFrame(left_col, text="Artwork")
        art_lf.pack(fill=tk.X)

        ttk.Label(art_lf, text="Main artwork:").pack(anchor=tk.W)
        self.selectedArtPath = tk.StringVar(value=str(config.DEFAULT_ART_PATH))
        ttk.Button(art_lf, text="Import Artwork",
                   command=lambda: self.choose_file(self.selectedArtPath)).pack(anchor=tk.W, pady=(4, 2))
        ttk.Label(art_lf, textvariable=self.selectedArtPath,
                  wraplength=210, justify="left",
                  font=("Helvetica", 8), foreground="#666666").pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(art_lf, text="Expansion artwork (optional):").pack(anchor=tk.W)
        self.selectedExpansionArtPath = tk.StringVar(value="")
        ttk.Button(art_lf, text="Import Expansion Artwork",
                   command=lambda: self.choose_file(self.selectedExpansionArtPath)).pack(anchor=tk.W, pady=(4, 2))
        ttk.Label(art_lf, textvariable=self.selectedExpansionArtPath,
                  wraplength=210, justify="left",
                  font=("Helvetica", 8), foreground="#666666").pack(anchor=tk.W)

        # ── Card Details ──────────────────────────────────────────────────
        details_lf = ttk.LabelFrame(right_col, text="Card Details")
        details_lf.pack(fill=tk.BOTH, expand=True)

        ttk.Label(details_lf, text="Title").pack(anchor=tk.W)
        self.titleGUI = ttk.Entry(details_lf, width=36)
        self.titleGUI.pack(anchor=tk.W, fill=tk.X, pady=(2, 8))

        ttk.Label(details_lf, text="Subtitle (optional)").pack(anchor=tk.W)
        self.subtitleGUI = ttk.Entry(details_lf, width=36)
        self.subtitleGUI.pack(anchor=tk.W, fill=tk.X, pady=(2, 8))

        ttk.Label(details_lf, text="Author (optional)").pack(anchor=tk.W)
        self.authorGUI = ttk.Entry(details_lf, width=36)
        self.authorGUI.pack(anchor=tk.W, fill=tk.X, pady=(2, 8))

        ttk.Label(details_lf, text="Description").pack(anchor=tk.W)
        self.descripGUI = tk.Text(details_lf, width=36, height=7, wrap="word",
                                   relief=tk.FLAT, bd=1,
                                   highlightthickness=1, highlightbackground="#CCCCCC",
                                   font=("Helvetica", 10))
        self.descripGUI.pack(anchor=tk.W, fill=tk.X, pady=(2, 8))

        ttk.Separator(details_lf, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 6))

        ttk.Label(details_lf, text="Generate card back").pack(anchor=tk.W)
        self.backCardFlagGUI = tk.BooleanVar(value=True)
        back_frame = tk.Frame(details_lf)
        back_frame.pack(anchor=tk.W, pady=(2, 0))
        ttk.Radiobutton(back_frame, text="Yes", variable=self.backCardFlagGUI, value=True).pack(side=tk.LEFT)
        ttk.Radiobutton(back_frame, text="No",  variable=self.backCardFlagGUI, value=False).pack(side=tk.LEFT, padx=(10, 0))

        # ── Separator ─────────────────────────────────────────────────────
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=14, pady=(8, 4))

        # ── Export buttons ────────────────────────────────────────────────
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=14, pady=8)
        ttk.Button(btn_frame, text="Export Card",
                   command=self.save_image, style="Primary.TButton").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="Export All Cards",
                   command=self.save_all_cards, style="Success.TButton").pack(side=tk.LEFT)

        # ── Separator ─────────────────────────────────────────────────────
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=14, pady=(0, 4))

        # ── Preview ───────────────────────────────────────────────────────
        preview_lf = ttk.LabelFrame(parent, text="Preview")
        preview_lf.pack(fill=tk.X, padx=14, pady=(4, 14))
        self.image_label = ttk.Label(preview_lf, text="Generating preview…")
        self.image_label.pack(pady=8)

        # ── Bindings ──────────────────────────────────────────────────────
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

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Cards…", command=self._import_cards)
        file_menu.add_command(label="Export Card List…", command=self._export_card_list)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Open README",
                              command=lambda: webbrowser.open(config.README_PATH.as_uri()))

        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Config", menu=config_menu)
        if sys.platform == "win32":
            config_menu.add_command(label="Edit config.py",
                                    command=lambda: subprocess.Popen(["notepad", str(config.CONFIG_PATH)]))
        else:
            config_menu.add_command(label="Edit config.py",
                                    command=lambda: subprocess.Popen(["gedit", str(config.CONFIG_PATH)]))
        config_menu.add_command(label="Reload Config",
                                command=lambda: importlib.reload(config) or self.update_image())

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

    def save_all_cards(self):
        if not self.cards:
            return
        directory = filedialog.askdirectory(title="Select export directory")
        if not directory:
            return
        output_dir = Path(directory)
        for i, card in enumerate(self.cards):
            title = card.get("title") or f"card_{i + 1}"
            safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title).strip() or f"card_{i + 1}"
            file_path = output_dir / f"{safe_title}.png"
            img = generate_card(
                card.get("card_type", 0),
                card.get("art_path", str(config.DEFAULT_ART_PATH)),
                card.get("card_value", "Random"),
                card.get("card_suit", 0),
                card.get("title", ""),
                card.get("subtitle", ""),
                card.get("author", ""),
                card.get("description", ""),
                card.get("back_card", True),
                card.get("expansion_art_path") or None,
                return_pil=True,
            )
            img.save(str(file_path), dpi=(config.DPI, config.DPI))

    def _import_cards(self):
        from tkinter import messagebox
        file_path = filedialog.askopenfilename(
            title="Import Cards",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                imported = json.load(f)
            if not isinstance(imported, list):
                messagebox.showerror("Import Error", "File does not contain a valid card list.")
                return
        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror("Import Error", f"Could not read file:\n{e}")
            return
        self.cards.extend(imported)
        self._save_cards_to_file()
        self._refresh_listbox()
        self._select_card(len(self.cards) - len(imported))
        messagebox.showinfo("Import", f"Imported {len(imported)} card(s).")

    def _export_card_list(self):
        from tkinter import messagebox
        if not self.cards:
            messagebox.showinfo("Export Card List", "No cards to export.")
            return
        file_path = filedialog.asksaveasfilename(
            title="Export Card List",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not file_path:
            return
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.cards, f, ensure_ascii=False, indent=2)

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
