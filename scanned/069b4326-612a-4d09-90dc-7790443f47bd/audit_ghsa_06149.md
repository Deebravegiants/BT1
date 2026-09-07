# [H] Defuddle vulnerable to XSS via unescaped attribute interpolation in site extractors

## Summary
Severity: High
Advisory: GHSA-jg4p-g6xj-4qmf
CVE: CVE-2026-61824
CWE: CWE-116, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-jg4p-g6xj-4qmf
Type: github-advisory

## Affected
- npm: `defuddle` — affected >=0 <0.19.1

## Details
## Summary

An Improper Neutralization of Input During Web Page Generation issue in the site extractor component allows an attacker-controlled attribute value to be injected into output HTML without escaping. An attacker who crafts a malicious HTML page or controls content on a matching domain can execute arbitrary scripts when a victim processes the page, resulting in Cross-Site Scripting (XSS).  This affects defuddle through 0.19.0 and has been patched in version 0.19.1.

## Impact

This vulnerability allows for Cross-Site Scripting (XSS) execution without needing to compromise external websites. Affected consumers include:
- Obsidian Web Clipper, 
- web services serving the parsed output directly as HTML, and 
- any downstream application rendering the unsanitized HTML results

## Patch
This issue has been patched in defuddle version 0.19.1. Users are encouraged to update to the latest release.

## References
- https://github.com/kepano/defuddle/security/advisories/GHSA-jg4p-g6xj-4qmf
- https://github.com/kepano/defuddle/pull/326
- https://github.com/kepano/defuddle/commit/baf2eaef61d334ef595b28c89e5c5e89e52daf7f
- https://github.com/kepano/defuddle
- https://github.com/kepano/defuddle/releases/tag/0.19.1
