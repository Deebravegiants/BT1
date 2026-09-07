# [M] symfony/ux-icons: XSS via unsanitized SVG content in local files and Iconify on-demand responses

## Summary
Severity: Medium
Advisory: GHSA-6v8j-33hc-mv84
CVE: CVE-2026-55877
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-6v8j-33hc-mv84
Type: github-advisory

## Affected
- Packagist: `symfony/ux-icons` — affected >=2.17.0 <2.36.1
- Packagist: `symfony/ux-icons` — affected >=3.0.0 <3.2.0

## Details
### Description

The `ux_icon()` Twig function is marked `is_safe=['html']`, so Twig never escapes its output. `Icon::toHtml()` inlines the SVG source verbatim into the page. Browsers execute `<script>` elements and `on*` event-handler attributes found inside inline SVG, making any unsanitized icon a vector for cross-site scripting.

Two code paths were affected. In the local file path, `Icon::fromFile()` only stripped `<script>` elements that were direct children of `<svg>`, leaving nested scripts and all `on*` attributes untouched despite a code comment claiming broader protection. In the Iconify on-demand path (enabled by default), the remote JSON `body` field was wrapped into an `Icon` object with no sanitization at all. Concrete attack vectors include a malicious SVG icon pack from a third-party theme or downloaded icon set, or a controlled Iconify endpoint configured via `iconify.endpoint` (including a poisoned cache).

### Resolution

Introducing an `IconFactory` that centralizes sanitization across every icon source before an `Icon` object is created. The sanitizer removes script-capable elements (`script`, `foreignObject`, `iframe`, `object`, `embed`), SMIL animations targeting `on*`, `href`, or `xlink:href` attributes, CDATA sections, processing instructions, all `on*` attributes, and `javascript:`, `vbscript:`, and `data:text/html` URL schemes. 
`<style>` elements are kept for theming but have any handlers stripped. Icons that contain none of these constructs are byte-for-byte identical after sanitization. 

### Credits

Symfony would like to thank Pascal Cescon for reporting the issue and Hugo Alliaume for providing the fix.

## References
- https://github.com/symfony/ux/security/advisories/GHSA-6v8j-33hc-mv84
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/ux-icons/CVE-2026-55877.yaml
- https://github.com/symfony/ux
