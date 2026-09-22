# [H] Authenticated Blind SQL Injection in DeleteRelationShip in SuiteCRM

## Summary
Severity: High
Advisory: BIT-suitecrm-2024-50332
Aliases: CVE-2024-50332, GHSA-53xh-mjmq-j35p
Ecosystem: Bitnami
Published: 2024-11-07
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-50332
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.7.1

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Insufficient input value validation causes Blind SQL injection in DeleteRelationShip. This issue has been addressed in versions 7.14.6 and 8.7.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-53xh-mjmq-j35p
- https://nvd.nist.gov/vuln/detail/CVE-2024-50332
