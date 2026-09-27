# [M] JustHTML has a Sanitizer Bypass (in Markdown)

## Summary
Severity: Medium
Advisory: GHSA-3rcm-vjrc-p45j
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-3rcm-vjrc-p45j
Type: github-advisory

## Affected
- PyPI: `justhtml` — affected >=0 <1.12.0

## Details
## Summary

`to_markdown()` does not sufficiently escape text content that looks like HTML. As a result, untrusted input that is safe in `to_html()` can become raw HTML in Markdown output.

This is not specific to tokenizer raw-text states like `<title>`, `<noscript>`, or `<plaintext>`, although those states can trigger the behavior. The root cause is broader: Markdown text serialization leaves angle brackets unescaped in text nodes.

## Details

When converting a parsed document to Markdown, text nodes are escaped for a small set of Markdown metacharacters, but HTML-significant characters such as `<` and `>` are preserved. That means content parsed as text, including entity-decoded text or text produced by RCDATA/RAWTEXT-style parsing, can be emitted into Markdown as raw HTML.

Examples of affected input include:

- Text produced from entity-decoded input such as `&lt;script&gt;...&lt;/script&gt;`
- Text inside elements like `<title>`, `<textarea>`, `<noscript>` (when parsed as raw text), and `<plaintext>`

This is distinct from actual `<script>` or `<style>` elements in the DOM. Those are already dropped by default in `to_markdown()` unless `html_passthrough=True`.

## Proof of Concept

### General case

```python
from justhtml import JustHTML

doc = JustHTML("<p>&lt;img src=x onerror=alert(1)&gt;</p>", fragment=True)

print(doc.to_html())
print()
print(doc.to_markdown())

## References
- https://github.com/EmilStenstrom/justhtml/security/advisories/GHSA-3rcm-vjrc-p45j
- https://github.com/EmilStenstrom/justhtml
