# [M] CVE-2026-75003

## Summary
Severity: Medium
Advisory: CVE-2026-75003
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75003
Type: osv

## Details
In Roundcube Webmail before 1.6.18 and 1.7.x before 1.7.3, an unclosed url() in a FuncIRI attribute of an SVG image could evade the remote image blocking, which may lead to information disclosure or privilege escalation.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.18
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.3
- https://roundcube.net/news/2026/08/09/security-updates-1.6.18-and-1.7.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75003.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75003
- https://github.com/roundcube/roundcubemail/commit/1cebea03474305d9f75a9a33d30880d290b5591b
- https://github.com/roundcube/roundcubemail/commit/440277c32e6d84f3d116153af1cc8454361a8a56
