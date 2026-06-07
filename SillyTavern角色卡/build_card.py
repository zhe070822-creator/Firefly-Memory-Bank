"""
Build SillyTavern / RisuAI character card PNG for Firefly.
Reads card_data.json, embeds it into a PNG's tEXt chunk.
Usage: python build_card.py
Output: Firefly.png (drag into SillyTavern)
"""

import json
import base64
from pathlib import Path
from PIL import Image
from PIL.PngImagePlugin import PngInfo

ROOT = Path(__file__).resolve().parent
DATA_IMAGES = ROOT.parent / "data" / "images"
CARD_JSON = ROOT / "card_data.json"
OUT_FILE = ROOT / "Firefly.png"

# -- choose source image --
SPLASH = DATA_IMAGES / "splash_art.png"
PORTRAIT = DATA_IMAGES / "portrait.png"
SRC_IMAGE = SPLASH if SPLASH.exists() else PORTRAIT

MAX_DIM = 900  # SillyTavern recommended max side

# -- load card data --
with open(CARD_JSON, "r", encoding="utf-8") as f:
    card = json.load(f)

# -- read, resize, embed --
img = Image.open(SRC_IMAGE).convert("RGBA")
w, h = img.size
if max(w, h) > MAX_DIM:
    ratio = MAX_DIM / max(w, h)
    img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

json_str = json.dumps(card, ensure_ascii=False, separators=(",", ":"))
b64 = base64.b64encode(json_str.encode("utf-8")).decode("ascii")

meta = PngInfo()
meta.add_text("chara", b64)
img.save(OUT_FILE, "PNG", pnginfo=meta)
img.close()

# -- verify --
verify = Image.open(OUT_FILE)
b64_back = verify.info.get("chara", "")
verify.close()

if b64_back:
    decoded = json.loads(base64.b64decode(b64_back))
    print(f"OK  {decoded['data']['name']}  |  {OUT_FILE.name}")
    print(f"JSON: {len(json_str)} chars  |  base64: {len(b64)} chars")
    print("Ready for SillyTavern.")
else:
    print("FAILED: tEXt chunk missing")
