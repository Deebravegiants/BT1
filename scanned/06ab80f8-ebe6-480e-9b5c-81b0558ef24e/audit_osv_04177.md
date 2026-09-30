# [M] Appsmith < 1.98 Unauthenticated Instance Configuration Disclosure via Management APIs

## Summary
Severity: Medium
Advisory: BIT-appsmith-2026-34411
Aliases: CVE-2026-34411, GHSA-qvvc-prjx-f85j
Ecosystem: Bitnami
Published: 2026-04-01
Source: https://osv.dev/vulnerability/BIT-appsmith-2026-34411
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=0 <1.98.0

## Details
Appsmith versions prior to 1.98 expose sensitive instance management API endpoints without authentication. Unauthenticated attackers can query endpoints like /api/v1/consolidated-api/view and /api/v1/tenants/current to retrieve configuration metadata, license information, and unsalted SHA-256 hashes of admin email domains for reconnaissance and targeted attack planning.

## References
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-qvvc-prjx-f85j
- https://nvd.nist.gov/vuln/detail/CVE-2026-34411
- https://www.vulncheck.com/advisories/appsmith-unauthenticated-instance-configuration-disclosure-via-management-apis
