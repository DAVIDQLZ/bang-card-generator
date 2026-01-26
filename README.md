# Bang! Card Generator

A desktop GUI application for creating **custom Bang! card game cards** with accurate physical dimensions and print-ready output. The tool lets you design action, item, and character cards using your own artwork, titles, descriptions, and expansion icons, with a live preview and export at a fixed DPI.

Built with **Python**, **Tkinter**, and **Pillow (PIL)**.

---

## ✨ Features

- 🎴 Supports multiple card types:
  - Action cards
  - Blue item cards
  - Green item cards
  - Character cards (3–6 lives)
- 🖼️ Import main artwork and optional expansion artwork
- ♠ Card value & suit selection (or random)
- 📝 Title, subtitle, author, and wrapped description text
- 🎨 Optional vignette effect on artwork
- 🔁 Automatic live preview while editing
- 🖨️ Print-ready export at configurable DPI (default: 300 DPI)
- 🃏 Optional card back generation
- ⚙️ Centralized configuration via `config.py`

---

## 📦 Requirements

- Python **3.10+** recommended
- Required Python packages:

```bash
pip install pillow
```

Tkinter is included with most standard Python installations.

---

## 🚀 Running the Application

Clone or download the project, then run:

```bash
python main.py
```

(The filename may differ depending on how you saved the script.)

---

## 🧭 How It Works

1. Choose a **card type** (action, item, or character)
2. Import **main artwork** (PNG or JPG)
3. Optionally import **expansion artwork**
4. Set **card value & suit** (if applicable)
5. Enter:
   - Title
   - Subtitle (optional)
   - Author (optional)
   - Description (auto-wrapped)
6. Enable or disable **card back** generation
7. Preview updates automatically
8. Export the final card as **PNG or JPG**

Exported images are saved with the configured DPI for printing.

---

## 🖨️ DPI & Physical Size

Card dimensions are defined in **millimeters** and converted to pixels using:

```
pixels = mm × DPI / 25.4
```

This guarantees correct physical size when printing.

You can change:
- Card size (mm)
- DPI
- Font sizes
- Colors

inside `config.py`.

---

## ⚙️ Configuration (`config.py`)

All visual and layout settings are centralized:

- Card dimensions (mm)
- DPI
- Font paths & sizes
- Text colors
- Template paths
- Suit icons
- Borders & card backs
- Vignette settings
- Default artwork path

You can edit the config from the menu:

**Config → Edit config.py**

Reload changes live using:

**Config → Reload Config**

---

## 📁 Project Structure (Typical)

```
project/
├── main.py
├── config.py
├── README.md
├── templates/
│   ├── action.png
│   ├── blue.png
│   ├── green.png
│   └── character_*.png
├── suits/
│   ├── hearts.png
│   ├── clubs.png
│   ├── diamonds.png
│   └── spades.png
├── fonts/
│   ├── title.ttf
│   ├── subtitle.ttf
│   └── body.ttf
├── borders/
│   └── border.png
└── backs/
    ├── back_playing.png
    └── back_character.png
```

Paths may vary depending on your setup.

---

## 🧠 Notes & Tips

- The preview is **scaled down** for screen display; exports are full resolution
- Use high-resolution artwork for best print quality
- Text wrapping is calculated dynamically based on font metrics
- Card back type is selected automatically based on card type

---

## ⚠️ Disclaimer

This is a **fan-made tool** for personal and creative use. Bang! is a trademark of its respective owners.

---

## 🛠️ Possible Future Improvements

- Zoom slider for preview
- Drag & drop artwork import
- Batch card generation
- PDF export with crop marks
- Localization support

---

Enjoy creating your custom Bang! cards 🤠🃏

