# [M] Roundcube Webmail: Insufficient HTML attachment sanitization in preview mode

## Summary
Severity: Medium
Advisory: GHSA-x4q5-8j5g-hpjc
CVE: CVE-2026-35539
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-x4q5-8j5g-hpjc
Type: github-advisory

## Affected
- Packagist: `roundcube/roundcubemail` — affected >=1.7-beta <1.7-rc5

## Details
An issue was discovered in Roundcube Webmail before 1.5.14 and 1.6.14. XSS exists because of insufficient HTML attachment sanitization in preview mode. A victim must preview a text/html attachment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35539
- https://github.com/roundcube/roundcubemail/commit/10a6d1fa8acac85c727b0a6ae4a6642bfa27bea1
- https://github.com/roundcube/roundcubemail/commit/1b30edf5369668c92fe91dae3d52e477c808aa4f
- https://github.com/roundcube/roundcubemail/commit/d742954ccbcdee7020f8f2e7c49ce0fca5a0efab
- https://github.com/roundcube/roundcubemail
- https://github.com/roundcube/roundcubemail/releases/tag/1.5.14
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.14
- https://github.com/roundcube/roundcubemail/releases/tag/1.7-rc5
- https://roundcube.net/news/2026/03/18/security-updates-1.7-rc5-1.6.14-1.5.14
