# [H] SuiteCRM authenticated SQL Injection in EmailUIAjax messages count controller

## Summary
Severity: High
Advisory: BIT-suitecrm-2024-36410
Aliases: CVE-2024-36410, GHSA-7jj8-m2wj-m6xq
Ecosystem: Bitnami
Published: 2024-06-12
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-36410
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.6.1

## Details
SuiteCRM is an open-source Customer Relationship Management (CRM) software application. In versions prior to 7.14.4 and 8.6.1, poor input validation allows for SQL Injection in EmailUIAjax messages count controller. Versions 7.14.4 and 8.6.1 contain a fix for this issue.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-7jj8-m2wj-m6xq
- https://nvd.nist.gov/vuln/detail/CVE-2024-36410
