# [M] SuiteCRM unauthenticated user password reset on php7

## Summary
Severity: Medium
Advisory: BIT-suitecrm-2024-36407
Aliases: CVE-2024-36407, GHSA-6p2f-wwx9-952r
Ecosystem: Bitnami
Published: 2024-06-12
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-36407
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.6.1

## Details
SuiteCRM is an open-source Customer Relationship Management (CRM) software application. In versions prior to 7.14.4 and 8.6.1, a user password can be reset from an unauthenticated attacker. The attacker does not get access to the new password. But this can be annoying for the user. This attack is also dependent on some password reset functionalities being enabled. It also requires the system using php 7, which is not an officially supported version. Versions 7.14.4 and 8.6.1 contain a fix for this issue.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-6p2f-wwx9-952r
- https://nvd.nist.gov/vuln/detail/CVE-2024-36407
