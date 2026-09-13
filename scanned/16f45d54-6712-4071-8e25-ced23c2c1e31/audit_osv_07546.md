# [H] SuiteCRM authenticated SQL Injection in TreeData entrypoint

## Summary
Severity: High
Advisory: BIT-suitecrm-2024-36409
Aliases: CVE-2024-36409, GHSA-pxq4-vw23-v73f
Ecosystem: Bitnami
Published: 2024-06-12
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-36409
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.6.1

## Details
SuiteCRM is an open-source Customer Relationship Management (CRM) software application. In versions prior to 7.14.4 and 8.6.1, poor input validation allows for SQL Injection in Tree data entry point. Versions 7.14.4 and 8.6.1 contain a fix for this issue.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-pxq4-vw23-v73f
- https://nvd.nist.gov/vuln/detail/CVE-2024-36409
