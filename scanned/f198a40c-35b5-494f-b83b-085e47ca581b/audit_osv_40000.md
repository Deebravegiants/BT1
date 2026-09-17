# [H] CVE-2026-48843

## Summary
Severity: High
Advisory: CVE-2026-48843
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-05-25
Source: https://osv.dev/vulnerability/CVE-2026-48843
Type: osv

## Details
Roundcube Webmail 1.6.x between 1.6.14 and 1.6.16,and 1.7.x before 1.7.1 has Insufficient Cascading Style Sheets (CSS) sanitization in HTML e-mail messages may lead to SSRF or Information Disclosure, e.g., if stylesheet links point to local network hosts. The issue stems from an insufficient fix for CVE-2026-35540.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.16
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.1
- https://roundcube.net/news/2026/05/24/security-updates-1.6.16-and-1.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48843.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48843
- https://github.com/roundcube/roundcubemail/commit/ab96c88bfd888866ec5e02190b19618db283923a
- https://github.com/roundcube/roundcubemail/commit/cb3fc9041e91640ba9ba49ee7b2147c176ebf5a1
