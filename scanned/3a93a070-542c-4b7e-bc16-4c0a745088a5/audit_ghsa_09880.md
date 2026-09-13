# [M] Roundcube Webmail: Remote image blocking feature can be bypassed via SVG content in an e-mail message

## Summary
Severity: Medium
Advisory: GHSA-w846-74jr-76cv
CVE: CVE-2026-35545
CWE: CWE-669
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-w846-74jr-76cv
Type: github-advisory

## Affected
- Packagist: `roundcube/roundcubemail` — affected >=1.7-beta <1.7-rc5

## Details
An issue was discovered in Roundcube Webmail before 1.5.15 and 1.6.15. The remote image blocking feature can be bypassed via SVG content in an e-mail message. This may lead to information disclosure or access-control bypass. This involves the animate element with attributeName=fill/filter/stroke.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35545
- https://github.com/roundcube/roundcubemail/commit/7ad62de184368bf42c0f522d1aacc030f5ddcc46
- https://github.com/roundcube/roundcubemail/commit/9d18d524f3cc211003fc99e2e54eed09a2f3da88
- https://github.com/roundcube/roundcubemail/commit/fe1320b199d3a2f58351bb699c9ed4316e73221b
- https://github.com/roundcube/roundcubemail
- https://github.com/roundcube/roundcubemail/releases/tag/1.5.15
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.15
- https://github.com/roundcube/roundcubemail/releases/tag/1.7-rc6
- https://roundcube.net/news/2026/03/29/security-updates-1.7-rc6-1.6.15-1.5.15
