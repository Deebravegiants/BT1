# [M] CVE-2026-75007

## Summary
Severity: Medium
Advisory: CVE-2026-75007
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75007
Type: osv

## Details
In Roundcube Webmail before 1.6.18 and 1.7.x before 1.7.3, the LDAP search filter was subject to injection via unescaped %u/%fu/%d substitution, which may lead to information disclosure or privilege escalation.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.18
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.3
- https://roundcube.net/news/2026/08/09/security-updates-1.6.18-and-1.7.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75007.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75007
- https://github.com/roundcube/roundcubemail/commit/0893e192adf803c7a5a89fafc80278257e1bcf65
- https://github.com/roundcube/roundcubemail/commit/e6cc1e121effeaec6d916feb4e019d2828924540
