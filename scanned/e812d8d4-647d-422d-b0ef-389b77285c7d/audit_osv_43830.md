# [H] CVE-2026-74997

## Summary
Severity: High
Advisory: CVE-2026-74997
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74997
Type: osv

## Details
In Roundcube Webmail before 1.6.18 and 1.7.x before 1.7.3, the cmd_learn driver of the markasjunk plugin is subject to remote code execution via crafted placeholder replacement values. This issue only affects Roundcube instances using the markasjunk plugin with its cmd_learn driver.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.18
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.3
- https://roundcube.net/news/2026/08/09/security-updates-1.6.18-and-1.7.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74997.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74997
- https://github.com/roundcube/roundcubemail/commit/14044f843cfacbe78b042f659e379d6b4497aa7c
- https://github.com/roundcube/roundcubemail/commit/495d211638f222336b20f4744545c53712426c2a
- https://github.com/roundcube/roundcubemail/commit/b8f90e28a46d42e79a69568cba897f8f4223d9cd
