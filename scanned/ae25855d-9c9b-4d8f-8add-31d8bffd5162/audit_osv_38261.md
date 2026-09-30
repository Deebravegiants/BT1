# [M] CVE-2026-35543

## Summary
Severity: Medium
Advisory: CVE-2026-35543
Aliases: GHSA-j2g6-8rvg-7mf6
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-35543
Type: osv

## Details
An issue was discovered in Roundcube Webmail before 1.5.14 and 1.6.14. The remote image blocking feature can be bypassed via SVG content (with animate attributes) in an e-mail message. This may lead to information disclosure or access-control bypass.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.5.14
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.14
- https://github.com/roundcube/roundcubemail/releases/tag/1.7-rc5
- https://roundcube.net/news/2026/03/18/security-updates-1.7-rc5-1.6.14-1.5.14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35543.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-35543
- https://github.com/roundcube/roundcubemail/commit/1a63e01542bff42aaa71c00c4c279a09ef31f20c
- https://github.com/roundcube/roundcubemail/commit/39471343ee081ce1d31696c456a2c163462daae3
- https://github.com/roundcube/roundcubemail/commit/82ab5eca7b332fce7a174b2b987f0957a66377cd
