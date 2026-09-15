# [M] WeKan < 8.19 LDAP Authentication Filter Injection

## Summary
Severity: Medium
Advisory: CVE-2026-25560
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-07
Source: https://osv.dev/vulnerability/CVE-2026-25560
Type: osv

## Details
WeKan versions prior to 8.19 contain an LDAP filter injection vulnerability in LDAP authentication. User-supplied username input is incorporated into LDAP search filters and DN-related values without adequate escaping, allowing an attacker to manipulate LDAP queries during authentication.

## References
- https://wekan.fi/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25560.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25560
- https://www.vulncheck.com/advisories/wekan-ldap-authentication-filter-injection
- https://github.com/wekan/wekan/commit/0b0e16c3eae28bbf453d33a81a9c58ce7db6d5bb
- https://github.com/wekan/wekan
