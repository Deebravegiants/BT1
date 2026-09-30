# [C] LDAP Injection in PAC4J

## Summary
Severity: Critical
Advisory: CVE-2026-40459
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40459
Type: osv

## Details
PAC4J is vulnerable to LDAP Injection in multiple methods. A low-privileged remote attacker can inject crafted LDAP syntax into ID-based search parameters, potentially resulting in unauthorized LDAP queries and arbitrary directory operations.

This issue was fixed in PAC4J versions 4.5.10, 5.7.10 and 6.4.1

## References
- https://cert.pl/en/posts/2026/04/CVE-2026-40458/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40459.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40459
- https://www.pac4j.org/blog/security-advisory-pac4j-core-and-ldap.html
