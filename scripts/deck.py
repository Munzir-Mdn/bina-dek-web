"""Bina atau semak dek HTML kendiri."""
import argparse
import json
import re
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ASSETS = Path(__file__).resolve().parents[1] / "assets"
LAYOUTS = {"focus": 4, "columns": 4, "sequence": 7}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def string(value):
    return isinstance(value, str) and bool(value.strip())


def validate(data):
    require(isinstance(data, dict), "Input mesti objek JSON.")
    require(string(data.get("title")), "Tajuk dek diperlukan.")
    lang = data.get("lang", "ms")
    require(isinstance(lang, str) and re.fullmatch(r"[a-zA-Z]{2,8}(?:-[a-zA-Z0-9]{1,8})*", lang),
            "Kod bahasa tidak sah.")
    slides = data.get("slides")
    require(isinstance(slides, list) and slides, "Sekurang-kurangnya satu slaid diperlukan.")
    ids = set()
    for index, slide in enumerate(slides, 1):
        prefix = f"Slaid {index}"
        require(isinstance(slide, dict), f"{prefix}: objek diperlukan.")
        key = slide.get("id")
        require(isinstance(key, str) and re.fullmatch(r"[a-z][a-z0-9-]*", key) and key not in ids,
                f"{prefix}: ID unik berhuruf kecil diperlukan.")
        ids.add(key)
        require(string(slide.get("title")), f"{prefix}: tajuk diperlukan.")
        layout = slide.get("layout", "focus")
        require(isinstance(layout, str) and layout in LAYOUTS, f"{prefix}: susun atur tidak sah.")
        for field in ("notes", "lead"):
            require(isinstance(slide.get(field, ""), str), f"{prefix}: {field} mesti teks.")
        seconds = slide.get("seconds", 0)
        require(type(seconds) is int and seconds >= 0, f"{prefix}: seconds mesti integer ≥ 0.")
        items = slide.get("items", [])
        require(isinstance(items, list) and len(items) <= LAYOUTS[layout],
                f"{prefix}: maksimum {LAYOUTS[layout]} item untuk {layout}.")
        for item in items:
            require(isinstance(item, dict) and string(item.get("label")) and string(item.get("text")),
                    f"{prefix}: item memerlukan label dan text.")
        sources = slide.get("sources", [])
        require(isinstance(sources, list), f"{prefix}: sources mesti senarai.")
        for source in sources:
            require(isinstance(source, dict) and string(source.get("label")) and string(source.get("url")),
                    f"{prefix}: sumber memerlukan label dan url.")
            url = urlsplit(source["url"])
            require(url.scheme == "https" and url.hostname and not re.search(r"\s", source["url"]),
                    f"{prefix}: gunakan URL HTTPS yang sah.")


def render_slide(slide, index):
    key = slide["id"]
    layout = slide.get("layout", "focus")
    title = escape(slide["title"])
    lead = escape(slide.get("lead", ""))
    items = "".join(
        f'<li><h2>{escape(item["label"])}</h2><p>{escape(item["text"])}</p></li>'
        for item in slide.get("items", [])
    )
    sources = "".join(
        f'<li><a href="{escape(ref["url"])}">{escape(ref["label"])}</a></li>'
        for ref in slide.get("sources", [])
    )
    item_tag = "ol" if layout == "sequence" else "ul"
    hidden = " hidden" if index else ""
    parts = [
        f'<section class="slide {layout}" id="slide-{key}" aria-labelledby="title-{key}"{hidden}>',
        f'<h1 id="title-{key}" tabindex="-1">{title}</h1>',
    ]
    if lead:
        parts.append(f'<p class="lead">{lead}</p>')
    if items:
        parts.append(f'<{item_tag} class="items">{items}</{item_tag}>')
    if sources:
        parts.append(f'<ul class="sources" aria-label="Sumber">{sources}</ul>')
    parts.append("</section>")
    return "\n".join(parts)


def build(data, style):
    validate(data)
    slides = data["slides"]
    notes = [{"id": slide["id"], "notes": slide.get("notes", ""), "seconds": slide.get("seconds", 0)}
             for slide in slides]
    notes_json = json.dumps(notes, ensure_ascii=False).replace("<", "\\u003c")
    sections = "\n".join(render_slide(slide, index) for index, slide in enumerate(slides))
    script = (ASSETS / "deck.js").read_text(encoding="utf-8")
    body = f"""<body><div class="shell">
<main id="deck">
{sections}
</main>
<nav class="toolbar" aria-label="Navigasi slaid">
<button id="prev" type="button">Sebelumnya</button>
<output id="count" aria-live="polite"></output>
<button id="next" type="button">Seterusnya</button>
<button id="toggle" type="button" aria-controls="presenter" aria-expanded="false">Pembentang</button>
</nav>
<aside id="presenter" aria-labelledby="presenter-title" hidden>
<h2 id="presenter-title">Nota pembentang</h2>
<p id="notes"></p>
<p><strong>Seterusnya</strong> <span id="upcoming"></span></p>
<p><strong>Masa slaid</strong> <span id="planned"></span></p>
<div class="toolbar">
<output id="clock" aria-label="Masa berlalu" aria-live="off">00:00</output>
<button id="timer" type="button">Mula</button>
<button id="reset" type="button">Set semula</button>
</div>
</aside>
</div>
<script id="deck-data" type="application/json">{notes_json}</script>
<script>
{script}
</script>
</body>"""
    template = (ASSETS / f"{style}.html").read_text(encoding="utf-8")
    values = {
        "TITLE": escape(data["title"]), "LANG": escape(data.get("lang", "ms")),
        "CSS": (ASSETS / "deck.css").read_text(encoding="utf-8"), "BODY": body,
    }
    return re.sub(r"\{\{([A-Z]+)\}\}", lambda match: values[match[1]], template)


class DeckParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.slides = []
        self.note_blocks = []
        self.in_data = False
        self.has_runtime = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        key = attrs.get("id")
        if key:
            require(key not in self.ids, f"ID berulang: {key}")
            self.ids.add(key)
        if tag == "section" and "slide" in attrs.get("class", "").split():
            self.slides.append((key, attrs.get("aria-labelledby"), "hidden" in attrs))
        self.in_data = tag == "script" and key == "deck-data"
        if tag == "script" and not self.in_data and "src" not in attrs:
            self.has_runtime = True

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_data = False

    def handle_data(self, data):
        if self.in_data:
            self.note_blocks.append(data)


def check(html, expected_seconds):
    parser = DeckParser()
    parser.feed(html)
    parser.close()
    required = {"deck", "prev", "next", "count", "toggle", "presenter", "notes",
                "planned", "upcoming", "clock", "timer", "reset", "deck-data"}
    require(required <= parser.ids and parser.has_runtime, "Komponen pelayar atau pembentang tiada.")
    require(parser.slides, "Tiada slaid.")
    notes = json.loads("".join(parser.note_blocks))
    require(isinstance(notes, list) and len(notes) == len(parser.slides), "Bilangan nota tidak padan.")
    total = 0
    for index, ((slide_id, heading, hidden), note) in enumerate(zip(parser.slides, notes)):
        require(heading in parser.ids and hidden == (index > 0), f"Paparan awal slaid {index + 1} tidak sah.")
        require(isinstance(note, dict) and string(note.get("id")) and slide_id == f'slide-{note["id"]}',
                f"ID nota slaid {index + 1} tidak padan.")
        require(isinstance(note.get("notes"), str) and type(note.get("seconds")) is int and note["seconds"] >= 0,
                f"Nota atau masa slaid {index + 1} tidak sah.")
        total += note["seconds"]
    if expected_seconds is not None:
        require(total == expected_seconds, f"Masa keseluruhan ialah {total}s, dijangka {expected_seconds}s.")
    print(f"Lulus semakan struktur: {len(notes)} slaid, {total}s masa dirancang.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    builder = commands.add_parser("build")
    builder.add_argument("input", type=Path)
    builder.add_argument("output", type=Path)
    builder.add_argument("--style", choices=("technical", "editorial"), default="technical")
    checker = commands.add_parser("check")
    checker.add_argument("input", type=Path)
    checker.add_argument("--expect-seconds", type=int)
    args = parser.parse_args()
    try:
        source = args.input.read_text(encoding="utf-8-sig")
        if args.command == "build":
            require(args.input.resolve() != args.output.resolve(), "Pilih laluan output yang berbeza.")
            args.output.write_text(build(json.loads(source), args.style), encoding="utf-8")
        else:
            check(source, args.expect_seconds)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Ralat: {error}\n")


if __name__ == "__main__":
    main()
