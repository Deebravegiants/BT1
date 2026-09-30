# [M] SuiteCRM authenticated Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: BIT-suitecrm-2024-36414
Aliases: CVE-2024-36414, GHSA-wg74-772c-8gr7
Ecosystem: Bitnami
Published: 2024-06-12
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-36414
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.6.1

## Details
SuiteCRM is an open-source Customer Relationship Management (CRM) software application. Prior to versions 7.14.4 and 8.6.1, a vulnerability in the connectors file verification allows for a server-side request forgery attack. Versions 7.14.4 and 8.6.1 contain a fix for this issue.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-wg74-772c-8gr7
- https://nvd.nist.gov/vuln/detail/CVE-2024-36414
