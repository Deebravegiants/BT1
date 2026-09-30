# [H] CVE-2026-62643

## Summary
Severity: High
Advisory: CVE-2026-62643
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-62643
Type: osv

## Details
In Roundcube Webmail before 1.6.17 and 1.7.x before 1.7.2, insufficient Cascading Style Sheets (CSS) sanitization in HTML e-mail messages may lead to SSRF or Information Disclosure, e.g., if stylesheet links point to local network hosts. NOTE: this issue exists because of insufficient fixes for CVE-2026-35540 and CVE-2026-48843.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.17
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.2
- https://roundcube.net/news/2026/07/05/security-updates-1.6.17-and-1.7.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62643.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-62643
- https://github.com/roundcube/roundcubemail/commit/294c7da6e7284166f040cef8607b677d459e0786
- https://github.com/roundcube/roundcubemail/commit/6d69e094d55d3a9a84dfb36edf6ca985311f0c1c
