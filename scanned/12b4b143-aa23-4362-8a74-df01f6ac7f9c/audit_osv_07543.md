# [M] SuiteCRM vulnerable to open redirects

## Summary
Severity: Medium
Advisory: BIT-suitecrm-2024-36406
Aliases: CVE-2024-36406, GHSA-hcw8-p37h-8hrv
Ecosystem: Bitnami
Published: 2024-06-12
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-36406
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.6.1

## Details
SuiteCRM is an open-source Customer Relationship Management (CRM) software application. In versions prior to 7.14.4 and 8.6.1, unchecked input allows for open re-direct. Versions 7.14.4 and 8.6.1 contain a fix for this issue.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-hcw8-p37h-8hrv
- https://nvd.nist.gov/vuln/detail/CVE-2024-36406
