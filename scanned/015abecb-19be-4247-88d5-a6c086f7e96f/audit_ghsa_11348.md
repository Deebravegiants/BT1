# [H] JustHTML is vulnerable to XSS via code fence breakout in <pre> content

## Summary
Severity: High
Advisory: GHSA-5vp3-3cg6-2rq3
CWE: CWE-79, CWE-80
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-5vp3-3cg6-2rq3
Type: github-advisory

## Affected
- PyPI: `justhtml` — affected >=0 <1.13.0

## Details
## Summary

`to_markdown()` is vulnerable when serializing attacker-controlled `<pre>` content. The `<pre>` handler emits a fixed three-backtick fenced code block, but writes decoded text content into that fence without choosing a delimiter longer than any backtick run inside the content.

An attacker can place backticks and HTML-like text inside a sanitized `<pre>` element so that the generated Markdown closes the fence early and leaves raw HTML outside the code block. When that Markdown is rendered by a CommonMark/GFM-style renderer that allows raw HTML, the HTML executes.

This is a bypass of the v1.12.0 Markdown hardening. That fix escaped HTML-significant characters for regular text nodes, but `<pre>` uses a separate serialization path and does not apply the same protection.

## Details

The vulnerable `<pre>` Markdown path:

- extracts decoded text from the `<pre>` subtree
- opens a fenced block with a fixed delimiter of ``````
- writes the decoded text directly into the output
- closes with another fixed ``````

Because the fence length is fixed, attacker-controlled content containing a backtick run of length 3 or more can terminate the code block. If the content also contains decoded HTML-like text such as `&lt;img ...&gt;`, that text appears outside the fence in the resulting Markdown and is treated as raw HTML by downstream Markdown renderers.

The issue is not that HTML-like text appears inside code blocks. The issue is that the serializer allows attacker-controlled `<pre>` text to break out of the fixed fence.

## Reproduction

```python
from justhtml import JustHTML

payload = "<pre>&#96;&#96;&#96;\n&lt;img src=x onerror=alert(1)&gt;</pre>"
doc = JustHTML(payload, fragment=True)  # default sanitize=True

print(doc.to_html(pretty=False))
# <pre>```
# &lt;img src=x onerror=alert(1)&gt;</pre>

print(doc.to_markdown())
# ```
# ```
# <img src=x onerror=alert(1)>
# ```

```

Rendered as CommonMark/GFM-style Markdown, that output is interpreted as:

1. Line 1 opens a fenced code block
2. Line 2 closes it
3. Line 3 is raw HTML outside the fence
4. Line 4 opens a new fence

## Impact

Applications that treat `JustHTML(..., sanitize=True).to_markdown()` output as safe for direct rendering in Markdown contexts may be exposed to XSS, depending on the downstream Markdown renderer's raw-HTML handling.

## Root Cause

The `<pre>` Markdown serializer uses a fixed fence instead of selecting a delimiter longer than the longest backtick run in the content.

## Fix

When serializing `<pre>` content to Markdown, choose a fence length longer than any backtick run present in the code block content, with a minimum length of 3.

## References
- https://github.com/EmilStenstrom/justhtml/security/advisories/GHSA-5vp3-3cg6-2rq3
- https://github.com/EmilStenstrom/justhtml/commit/f35f8f723c713bd8f912d86e9ec6881275ff5af9
- https://github.com/EmilStenstrom/justhtml
- https://github.com/EmilStenstrom/justhtml/releases/tag/v1.13.0
