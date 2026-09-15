# [M] CVE-2026-75000

## Summary
Severity: Medium
Advisory: CVE-2026-75000
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75000
Type: osv

## Details
In Roundcube Webmail before 1.6.18 and 1.7.x before 1.7.3, improper HTML/CSS sanitization of the SVG animate "by" attribute may lead to remote image blocking bypass, which in turn may lead to information disclosure or privilege escalation.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.18
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.3
- https://roundcube.net/news/2026/08/09/security-updates-1.6.18-and-1.7.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75000.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75000
