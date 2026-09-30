# [M] Kanboard LDAP Injection Vulnerability can Lead to User Enumeration and Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-21880
Aliases: GHSA-v66r-m28r-wmq7
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2026-21880
Type: osv

## Details
Kanboard is project management software focused on Kanban methodology. Versions 1.2.48 and below have an LDAP Injection vulnerability in the LDAP authentication mechanism. User-supplied input is directly substituted into LDAP search filters without proper sanitization, allowing attackers to enumerate all LDAP users, discover sensitive user attributes, and perform targeted attacks against specific accounts. This issue is fixed in version 1.2.49.

## References
- https://github.com/kanboard/kanboard/releases/tag/v1.2.49
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21880.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-v66r-m28r-wmq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-21880
- https://github.com/kanboard/kanboard/commit/dd374079f7c2d1dab74c1680960e684ff8668586
