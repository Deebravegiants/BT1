# [M] CVE-2026-75004

## Summary
Severity: Medium
Advisory: CVE-2026-75004
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75004
Type: osv

## Details
In Roundcube Webmail before 1.6.18 and 1.7.x before 1.7.3, improper rule name quoting could lead to managesieve_disabled_actions setting bypass via a crafted rule name in a Sieve script. This issue only affects Roundcube instances using the managesieve plugin.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.18
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.3
- https://roundcube.net/news/2026/08/09/security-updates-1.6.18-and-1.7.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75004.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75004
