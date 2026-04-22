# pdf2htmlEX HTML Structure Guide

This document describes the HTML structure produced by pdf2htmlEX, so you can accurately extract text with page numbers for KB citations.

## Page Structure

Each PDF page becomes a `<div>` with class `pf`:

```html
<div id="pf1" class="pf w0 h0" data-page-no="1">
  <!-- page 1 content -->
</div>
<div id="pf2" class="pf w0 h0" data-page-no="2">
  <!-- page 2 content -->
</div>
```

- `id="pfN"` — page identifier (hex for pages >= 100: `pf64` = page 100)
- `data-page-no="N"` — same identifier as attribute (**hex** for pages >= 100)
- Total pages = number of `.pf` divs (use `class="pf "` to count, NOT `data-page-no="\d+"`)

**Important: page numbering is hexadecimal for pages 100+.**

```
Page 1-99:    data-page-no="1" ... data-page-no="99"    (decimal)
Page 100:     data-page-no="64"                          (0x64 = 100)
Page 200:     data-page-no="c8"                          (0xC8 = 200)
Page 245:     data-page-no="f5"                          (0xF5 = 245)
```

To get the actual 1-indexed page number: `int(data_page_no, 16)` for hex values, `int(data_page_no)` for decimal. A simple rule: if the value contains letters (a-f), it's hex.

## Text Structure

Inside each page, text is in `<div class="t">` elements:

```html
<div class="t m3 x16 h6 y31 ff1 fs2 fc0 sc0 ls3 ws5">
  Operating revenue (RMB)
  <span class="_ _8"> </span>
  <span class="ws6">194,984,598,000.00</span>
</div>
```

Key points:
- Text is split across many `<span>` elements for precise positioning
- **Spacing spans** (`<span class="_ _N">`) simulate character spacing — they contain a space or are empty
- CSS classes (`ff1`, `fs2`, etc.) control font family, size, color — ignore them for text extraction

## PUA Characters (Private Use Area)

pdf2htmlEX uses custom fonts where some characters are mapped to Unicode PUA range (U+E000–U+F8FF). In the DOM:
- These render visually as spaces or specific glyphs (using the embedded font)
- But their `textContent` contains PUA codepoints, not regular characters

**You MUST replace PUA characters with spaces** when extracting text, otherwise:
- Text appears glued together ("Totalrevenues" instead of "Total revenues")
- `anchor` won't match DOM textContent during replay

## Soft Hyphens and Ligatures

pdf2htmlEX may insert:
- **Soft hyphens** (U+00AD) — invisible hyphens at word-break points. Remove them.
- **Ligatures** — single characters representing multiple letters (e.g., `ﬁ` = `fi`, `ﬂ` = `fl`). replay.js handles these automatically, but be aware they exist in `textContent`.

## How to Extract Text with Page Numbers

Use this Python pattern to extract text **per page**:

```python
import re
from html.parser import HTMLParser

class PageTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pages = {}       # {page_num: text}
        self.current_page = 0
        self.skip = False
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip = True
            return
        attrs_dict = dict(attrs)
        classes = attrs_dict.get('class', '')
        # Detect page boundary
        if tag == 'div' and 'pf ' in f'{classes} ':
            # Save previous page
            if self.current_page > 0 and self.chunks:
                self.pages[self.current_page] = ''.join(self.chunks)
            self.current_page += 1
            self.chunks = []

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = False

    def handle_data(self, data):
        if not self.skip and self.current_page > 0:
            self.chunks.append(data)

    def finish(self):
        if self.current_page > 0 and self.chunks:
            self.pages[self.current_page] = ''.join(self.chunks)

with open("document.html", encoding="utf-8") as f:
    html = f.read()

parser = PageTextExtractor()
parser.feed(html)
parser.finish()

# Clean each page's text
for page_num in sorted(parser.pages):
    text = parser.pages[page_num]
    # Replace PUA characters with spaces
    text = re.sub(r'[\ue000-\uf8ff]', ' ', text)
    # Remove soft hyphens
    text = text.replace('\u00ad', '')
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    print(f"--- Page {page_num} ---")
    print(text[:500])
    print()
```

## Rules for `anchor` and `quoted_text`

### anchor
- Must be a **verbatim substring** of the page's `textContent` (after PUA replacement and whitespace normalization)
- 5–10 words, uniquely identifies the cited content on that page
- Do NOT re-join hyphenated words or edit the text in any way

### quoted_text
- A longer passage (1–3 sentences) surrounding the anchor
- Must also be a verbatim substring of the same page's text
- If you can't find a longer passage, set it equal to anchor

### page
- The **1-indexed page number** where you found the text
- Use sequential counting (1st `.pf` div = page 1, 2nd = page 2, etc.)
- Do NOT use `data-page-no` directly — it switches to hex at page 100 (e.g., `data-page-no="64"` is page 100, not page 64)
- Never guess — always extract from the page structure

## How replay.js Matches Text

Understanding this helps you write better anchors:

1. replay.js iterates all `<div class="pf">` elements
2. For each page, it gets `textContent` and normalizes it (collapse whitespace, lowercase)
3. It also handles: PUA→space, ligature expansion, soft hyphen removal
4. It searches for the anchor as a substring
5. First page that contains the anchor wins — it scrolls there and highlights

**Implication**: if the same text appears on multiple pages, replay.js highlights the **first occurrence**. Make your anchor specific enough to be unique, or ensure `page` is correct so the right page is found first.

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|------------|-----|
| Extracting text without PUA replacement | "Totalrevenues" — anchor won't match | Always replace `[\ue000-\uf8ff]` with space |
| Extracting all text at once (no page split) | Can't determine correct `page` number | Extract per `.pf` div |
| Editing or reformatting extracted text | anchor diverges from DOM textContent | Use text exactly as extracted |
| Using `WebFetch` instead of `curl` | Returns only CSS (HTML too large) | Always use `curl` to download, then extract locally |
| Guessing page number | Replay scrolls to wrong page, no highlight | Count which `.pf` div contains the text |
| Using `data-page-no` as page number | Pages 100+ have hex values (`64`=100, `c8`=200) — wrong page number | Count `.pf` divs sequentially (1, 2, 3...) |
| Counting pages with `re.findall(r'data-page-no="\d+"')` | Misses hex pages (100+), reports fewer pages than exist | Count `class="pf "` occurrences instead |
