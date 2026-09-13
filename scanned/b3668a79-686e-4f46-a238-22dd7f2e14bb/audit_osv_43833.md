# [H] CVE-2026-75002

## Summary
Severity: High
Advisory: CVE-2026-75002
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75002
Type: osv

## Details
In Roundcube Webmail before 1.6.18 and 1.7.x before 1.7.3, mail search and LITERAL+ byte-count desynchronization could lead to information disclosure or privilege escalation via IMAP command injection.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.18
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.3
- https://roundcube.net/news/2026/08/09/security-updates-1.6.18-and-1.7.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75002.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75002
- https://github.com/roundcube/roundcubemail/commit/404d43f1b0125319c3cf8c9e3df39074c0cb80ad
- https://github.com/roundcube/roundcubemail/commit/73233abe581b3b31cefd00041c7086c40e1793ea
