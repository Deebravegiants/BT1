# [M] CVE-2026-75006

## Summary
Severity: Medium
Advisory: CVE-2026-75006
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75006
Type: osv

## Details
In Roundcube Webmail before 1.6.18 and 1.7.x before 1.7.3, insufficient Cascading Style Sheets (CSS) sanitization in HTML e-mail messages may lead to SSRF or Information Disclosure, e.g., if stylesheet links point to local network hosts. This issue exists because of insufficient fixes for CVE-2026-35540, CVE-2026-48843 and CVE-2026-62643.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.18
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.3
- https://roundcube.net/news/2026/08/09/security-updates-1.6.18-and-1.7.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75006.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75006
- https://github.com/roundcube/roundcubemail/commit/7e10ca0110b7c9aa1b7850b843bb6625e47bbe00
- https://github.com/roundcube/roundcubemail/commit/8a92380b06b5df1481e034c4f40d6a6546c21223
- https://github.com/roundcube/roundcubemail/commit/92f85c883594e5be757154f94548a9ba903455c9
- https://github.com/roundcube/roundcubemail/commit/c111b72950cd2bf57d6b86cd129568d90403322d
