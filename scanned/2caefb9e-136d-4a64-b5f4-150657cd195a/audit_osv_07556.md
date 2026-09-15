# [M] SuiteCRM has wrong deletion permission checks on API delete call

## Summary
Severity: Medium
Advisory: BIT-suitecrm-2024-45392
Aliases: CVE-2024-45392, GHSA-8qfx-h7pm-2587
Ecosystem: Bitnami
Published: 2024-09-07
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-45392
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.6.2

## Details
SuiteCRM is an open-source customer relationship management (CRM) system. Prior to version 7.14.5 and 8.6.2, insufficient access control checks allow a threat actor to delete records via the API. Versions 7.14.5 and 8.6.2 contain a patch for the issue.

## References
- https://docs.suitecrm.com/admin/releases/7.14.x/#_7_14_5
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-8qfx-h7pm-2587
- https://nvd.nist.gov/vuln/detail/CVE-2024-45392
