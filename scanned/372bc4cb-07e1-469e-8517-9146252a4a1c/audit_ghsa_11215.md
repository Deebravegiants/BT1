# [H] SVG Dimension Capping Bypass via XML Comment Injection in @dicebear/converter ensureSize()

## Summary
Severity: High
Advisory: GHSA-7j2x-32w6-p43p
CVE: CVE-2026-33418
CWE: CWE-185
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-7j2x-32w6-p43p
Type: github-advisory

## Affected
- npm: `@dicebear/converter` — affected >=0 <9.4.2

## Details
## Summary

The `ensureSize()` function in `@dicebear/converter` used a regex-based approach to rewrite SVG `width`/`height` attributes, capping them at 2048px to prevent denial of service. This size capping could be bypassed by crafting SVG input that causes the regex to match a non-functional occurrence of `<svg` before the actual SVG root element. When the SVG is subsequently rendered via `@resvg/resvg-js` on the Node.js code path, it renders at the attacker-specified dimensions, potentially causing out-of-memory crashes.

## Details

The vulnerable function used `String.prototype.replace()` with a non-global regex to find and rewrite the first `<svg` tag's dimensions. Since the regex does not distinguish between `<svg` appearing inside non-element XML constructs and the actual SVG root element, a crafted input can cause the regex to match a decoy instead of the real element, leaving the actual SVG dimensions unclamped.

In the Node.js rendering path, `renderAsync` from `@resvg/resvg-js` was called without a `fitTo` constraint, so it would render at whatever dimensions the SVG element specified — potentially allocating gigabytes of memory.

The browser code path is **not** vulnerable because it uses the clamped `size` return value from `ensureSize()` to set `canvas.width` and `canvas.height` directly.

## Impact

Any application that passes untrusted or user-supplied SVG content through `@dicebear/converter`'s Node.js conversion functions (`toPng`, `toJpeg`, `toWebp`, `toAvif`) is vulnerable to denial of service via excessive memory allocation. Note that `@dicebear/converter` can be used independently of DiceBear's avatar generation — any SVG string can be passed to the conversion functions.

The impact is limited to availability — there is no data disclosure or integrity impact. The browser code path is not affected.

## Fix

The regex-based approach has been replaced with XML-aware processing using `fast-xml-parser` to correctly identify and modify the SVG root element's attributes. Additionally, a `fitTo` constraint has been added to the `renderAsync` call as defense-in-depth, ensuring the rendered output is always bounded regardless of SVG content.

## References
- https://github.com/dicebear/dicebear/security/advisories/GHSA-7j2x-32w6-p43p
- https://nvd.nist.gov/vuln/detail/CVE-2026-33418
- https://github.com/dicebear/dicebear
