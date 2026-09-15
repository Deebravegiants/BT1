# [H] SuiteCRM is Vulnerable to PHP Object Injection in Reports

## Summary
Severity: High
Advisory: CVE-2025-54785
Aliases: GHSA-53cp-mpfw-qj67
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-06
Source: https://osv.dev/vulnerability/CVE-2025-54785
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. In versions 7.14.6  and 8.8.0, user-supplied input is not validated/sanitized before it is passed to the unserialize function, which could lead to penetration, privilege escalation, sensitive data exposure, Denial of Service, cryptomining and ransomware. This issue is fixed in version 7.14.7 and 8.8.1.

## References
- https://docs.suitecrm.com/admin/releases/7.14.x/#_7_14_7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54785.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-53cp-mpfw-qj67
- https://nvd.nist.gov/vuln/detail/CVE-2025-54785
