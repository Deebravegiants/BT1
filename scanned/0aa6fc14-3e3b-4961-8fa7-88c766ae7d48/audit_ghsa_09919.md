# [M] Roundcube Webmail: Insufficient CSS sanitization in HTML e-mail messages

## Summary
Severity: Medium
Advisory: GHSA-vxg2-hhgr-37fx
CVE: CVE-2026-35540
CWE: CWE-669, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-vxg2-hhgr-37fx
Type: github-advisory

## Affected
- Packagist: `roundcube/roundcubemail` — affected >=1.7-beta <1.7-rc5

## Details
An issue was discovered in Roundcube Webmail 1.6.0 before 1.6.14. Insufficient Cascading Style Sheets (CSS) sanitization in HTML e-mail messages may lead to SSRF or Information Disclosure, e.g., if stylesheet links point to local network hosts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35540
- https://github.com/roundcube/roundcubemail/commit/27ec6cc9cb25e1ef8b4d4ef39ce76d619caa6870
- https://github.com/roundcube/roundcubemail/commit/579b68eff90650a5c782e153debd66c765648942
- https://github.com/roundcube/roundcubemail
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.14
- https://github.com/roundcube/roundcubemail/releases/tag/1.7-rc5
- https://roundcube.net/news/2026/03/18/security-updates-1.7-rc5-1.6.14-1.5.14
