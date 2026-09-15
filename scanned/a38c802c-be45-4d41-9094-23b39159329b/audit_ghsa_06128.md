# [H] Snipe-IT vulnerable to directory traversal in displaySig

## Summary
Severity: High
Advisory: GHSA-c6f4-wj38-m3g3
CVE: CVE-2026-55474
CWE: CWE-23
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-c6f4-wj38-m3g3
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.5.0

## Details
### Impact
The `displaySig` action in `ActionlogController` serves signature image files from a private upload directory. The filename parameter from the HTTP route is concatenated directly into a filesystem path with no sanitization, allowing an authenticated attacker to traverse outside the intended directory and read arbitrary files accessible to the web server process.


Reported by https://github.com/securin-public

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-c6f4-wj38-m3g3
- https://nvd.nist.gov/vuln/detail/CVE-2026-55474
- https://github.com/grokability/snipe-it/pull/18927
- https://github.com/grokability/snipe-it/commit/cd69a7ea53e030e6e05f08be18daac672c8c4121
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.5.0
