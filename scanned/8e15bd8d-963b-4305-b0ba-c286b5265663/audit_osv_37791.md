# [H] SuiterCRM has LDAP Filter Injection in Authentication Module

## Summary
Severity: High
Advisory: CVE-2026-33289
Aliases: GHSA-26vx-rj47-x599
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-33289
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Prior to versions 7.15.1 and 8.9.3, an LDAP Injection vulnerability exists in the SuiteCRM authentication flow. The application fails to properly sanitize user-supplied input before embedding it into the LDAP search filter. By injecting LDAP control characters, an unauthenticated attacker can manipulate the query logic, which can lead to authentication bypass or information disclosure. Versions 7.15.1 and 8.9.3 patch the issue.

## References
- https://docs.suitecrm.com/admin/releases/7.15.x
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33289.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-26vx-rj47-x599
- https://nvd.nist.gov/vuln/detail/CVE-2026-33289
