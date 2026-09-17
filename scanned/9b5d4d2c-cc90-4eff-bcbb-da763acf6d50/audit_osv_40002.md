# [M] CVE-2026-48845

## Summary
Severity: Medium
Advisory: CVE-2026-48845
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-25
Source: https://osv.dev/vulnerability/CVE-2026-48845
Type: osv

## Details
In Roundcube Webmail 1.6.x between 1.6.14 and 1.6.16 and 1.7.x before 1.7.1, remote image blocking was not honored for URLs pointing to local/private destinations, which may lead to information disclosure or privilege escalation via a text/html email message.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.16
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.1
- https://roundcube.net/news/2026/05/24/security-updates-1.6.16-and-1.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48845.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48845
- https://github.com/roundcube/roundcubemail/commit/7b52353653a67e6073b97d70eb94047132b78556
- https://github.com/roundcube/roundcubemail/commit/d82b8c6cd06c378eca6d647ccd548f4ff1c68659
