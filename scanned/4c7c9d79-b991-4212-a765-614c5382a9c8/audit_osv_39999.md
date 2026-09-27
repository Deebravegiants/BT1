# [H] CVE-2026-48842

## Summary
Severity: High
Advisory: CVE-2026-48842
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-25
Source: https://osv.dev/vulnerability/CVE-2026-48842
Type: osv

## Details
Roundcube Webmail 1.6.x before 1.6.16 and 1.7.x before 1.7.1 has Pre-authentication SQL injection in the virtuser_query plugin via a preg_replace() backslash escape bypass.

## References
- http://www.openwall.com/lists/oss-security/2026/06/03/17
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.16
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.1
- https://roundcube.net/news/2026/05/24/security-updates-1.6.16-and-1.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48842.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48842
- https://github.com/roundcube/roundcubemail/commit/3406183a9976e36f992d3468f37d0e2346526ee9
- https://github.com/roundcube/roundcubemail/commit/87124cc7136a48b5fa9d2b40dfead6e9dcaeaf4b
