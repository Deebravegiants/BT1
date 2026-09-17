# [M] CVE-2026-48846

## Summary
Severity: Medium
Advisory: CVE-2026-48846
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-25
Source: https://osv.dev/vulnerability/CVE-2026-48846
Type: osv

## Details
In Roundcube Webmail 1.6.x before 1.6.16 and 1.7.x before 1.7.1, the remote image blocking feature can be bypassed via a crafted CSS var() value in an e-mail message, which may lead to information disclosure or access-control bypass.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.16
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.1
- https://roundcube.net/news/2026/05/24/security-updates-1.6.16-and-1.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48846.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48846
- https://github.com/roundcube/roundcubemail/commit/59cca80908a61e662c5f81741449e9aeb91e8abe
- https://github.com/roundcube/roundcubemail/commit/852350486b88b35b8544e8a630fad89e99e2150a
