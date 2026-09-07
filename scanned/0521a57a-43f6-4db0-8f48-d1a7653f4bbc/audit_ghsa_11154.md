# [M] JustHTML Affected by Mutation XSS via Literal Text Serialization in Raw Text Elements (style/script)

## Summary
Severity: Medium
Advisory: GHSA-qvc2-mg72-jjhx
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-qvc2-mg72-jjhx
Type: github-advisory

## Affected
- PyPI: `justhtml` — affected >=0 <1.12.0

## Details
## Summary

Sanitized DOM trees can be unsafe to serialize when a custom policy allows raw-text elements such as `<style>` or `<script>`.

The issue affects DOM trees that are constructed or modified programmatically and then passed through `sanitize_dom()` with a policy that keeps these elements. Text nodes inside `<style>` and `<script>` are serialized literally, so attacker-controlled text containing the matching closing tag sequence can break out of the raw-text context and inject HTML into the serialized output.

The default sanitization policy is not affected because it drops the contents of `style` and `script`.

## Details

The root cause is in HTML serialization of raw-text elements. In serialize.py, text children of `script` and `style` are emitted verbatim:

```python
_LITERAL_TEXT_SERIALIZATION_ELEMENTS = frozenset({"script", "style"})

def _serialize_text_for_parent(text: str | None, parent_name: str | None) -> str:
    if not text:
        return ""
    if parent_name in _LITERAL_TEXT_SERIALIZATION_ELEMENTS:
        return text
    return _escape_text(text)

## References
- https://github.com/EmilStenstrom/justhtml/security/advisories/GHSA-qvc2-mg72-jjhx
- https://github.com/EmilStenstrom/justhtml
