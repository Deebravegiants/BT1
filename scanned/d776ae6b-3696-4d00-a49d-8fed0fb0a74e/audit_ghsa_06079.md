# [M] Snipe-IT vulnerable to stored XSS via Markdown custom field 

## Summary
Severity: Medium
Advisory: GHSA-r52f-r9v5-66xr
CVE: CVE-2026-55464
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-r52f-r9v5-66xr
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
CommonMark is configured with `html_input => 'escape'`, which blocks raw HTML injection. However, javascript: URIs in Markdown hyperlinks are not sanitized. A user with `assets.edit` permission can inject a malicious link into any markdown-textarea custom field. Any user who opens the asset detail page and clicks the link executes arbitrary JavaScript in their browser session.

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-r52f-r9v5-66xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-55464
- https://github.com/grokability/snipe-it/commit/006981cccffce1739e24d3b680b676f772f40e2d
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
