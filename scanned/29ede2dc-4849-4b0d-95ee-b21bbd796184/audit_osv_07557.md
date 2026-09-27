# [H] Authenticated SQL injection in AM_ProjectTemplates controller in SuiteCRM

## Summary
Severity: High
Advisory: BIT-suitecrm-2024-49772
Aliases: CVE-2024-49772, GHSA-4xj8-hr85-hm3m
Ecosystem: Bitnami
Published: 2024-11-07
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-49772
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.7.1

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. In SuiteCRM versions 7.14.4, poor input validation allows authenticated user do a SQL injection attack. Authenticated user with low pivilege can leak all data in database. This issue has been addressed in releases 7.14.6 and 8.7.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-4xj8-hr85-hm3m
- https://nvd.nist.gov/vuln/detail/CVE-2024-49772
