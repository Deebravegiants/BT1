# [M] SuiteCRM: Legacy iCal service allows unauthenticated access to meeting data

## Summary
Severity: Medium
Advisory: BIT-suitecrm-2025-54786
Aliases: CVE-2025-54786, GHSA-rf2v-4mv3-qcgm
Ecosystem: Bitnami
Published: 2025-08-18
Source: https://osv.dev/vulnerability/BIT-suitecrm-2025-54786
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.8.0 <8.8.1

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. In versions 7.14.6 and 8.8.0, the broken authentication in the legacy iCal service allows unauthenticated access to meeting data. An unauthenticated actor can view any user's meeting (calendar event) data given their username, related functionality allows user enumeration. This is fixed in versions 7.14.7 and 8.8.1.

## References
- https://docs.suitecrm.com/8.x/admin/releases/8.8
- https://github.com/SuiteCRM/SuiteCRM-Core/security/advisories/GHSA-rf2v-4mv3-qcgm
- https://nvd.nist.gov/vuln/detail/CVE-2025-54786
