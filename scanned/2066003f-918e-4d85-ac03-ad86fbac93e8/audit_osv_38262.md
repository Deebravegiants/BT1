# [M] CVE-2026-35544

## Summary
Severity: Medium
Advisory: CVE-2026-35544
Aliases: GHSA-xpqh-grpw-4xmg
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-35544
Type: osv

## Details
An issue was discovered in Roundcube Webmail before 1.5.14 and 1.6.14. Insufficient Cascading Style Sheets (CSS) sanitization in HTML e-mail messages may lead to a fixed-position mitigation bypass via the use of !important.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.5.14
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.14
- https://github.com/roundcube/roundcubemail/releases/tag/1.7-rc5
- https://roundcube.net/news/2026/03/18/security-updates-1.7-rc5-1.6.14-1.5.14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35544.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-35544
- https://github.com/roundcube/roundcubemail/commit/099009b9c8e1d3c636fb9a5af72f7c2596018662
- https://github.com/roundcube/roundcubemail/commit/226811a1c974271dbedca72672923abaff8191c0
- https://github.com/roundcube/roundcubemail/commit/57dec0c127b98e0c8e3b9c26c80049b9c4bcaea7
