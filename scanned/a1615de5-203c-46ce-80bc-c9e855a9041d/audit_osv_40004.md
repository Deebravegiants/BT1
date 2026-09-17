# [H] CVE-2026-48848

## Summary
Severity: High
Advisory: CVE-2026-48848
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-05-25
Source: https://osv.dev/vulnerability/CVE-2026-48848
Type: osv

## Details
Roundcube Webmail 1.6.x before 1.6.16 and 1.7.x before 1.7 has insufficient HTML sanitization that could lead to Cascading Style Sheets (CSS) injection via an SVG document that has an animate element with the attributeName attribute.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.16
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.1
- https://roundcube.net/news/2026/05/24/security-updates-1.6.16-and-1.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48848.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48848
- https://github.com/roundcube/roundcubemail/commit/58e5263f341e6a418774fb6d2643669a3c4d8a27
- https://github.com/roundcube/roundcubemail/commit/c960d102472dc579e15907d5bcdc3103a090ccf9
