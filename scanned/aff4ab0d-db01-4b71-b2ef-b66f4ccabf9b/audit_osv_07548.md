# [C] SuiteCRM unauthenticated SQL Injection

## Summary
Severity: Critical
Advisory: BIT-suitecrm-2024-36412
Aliases: CVE-2024-36412, GHSA-xjx2-38hv-5hh8
Ecosystem: Bitnami
Published: 2024-06-12
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-36412
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.6.1

## Details
SuiteCRM is an open-source Customer Relationship Management (CRM) software application. Prior to versions 7.14.4 and 8.6.1, a vulnerability in events response entry point allows for a SQL injection attack. Versions 7.14.4 and 8.6.1 contain a fix for this issue.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-xjx2-38hv-5hh8
- https://nvd.nist.gov/vuln/detail/CVE-2024-36412
