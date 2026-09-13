# [H] SuiteCRM: Authenticated Blind SQL Injection in InboundEmail module

## Summary
Severity: High
Advisory: CVE-2025-54788
Aliases: GHSA-v3m9-8wg7-c72x
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-06
Source: https://osv.dev/vulnerability/CVE-2025-54788
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. In versions and below, the InboundEmail module allows the arbitrary execution of queries in the backend database, leading to SQL injection. This can have wide-reaching implications on confidentiality, integrity, and availability, as database data can be retrieved, modified, or removed entirely. This issue is fixed in version 7.14.7.

## References
- https://docs.suitecrm.com/admin/releases/7.14.x/#_7_14_7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54788.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-v3m9-8wg7-c72x
- https://nvd.nist.gov/vuln/detail/CVE-2025-54788
