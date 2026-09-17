# [M] Keycloak-services: keycloak-services: fgap v2 client scope assignment bypass via clientresource

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-14614
Aliases: CVE-2026-14614
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-14614
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.5

## Details
A flaw was found in the ClientResource component of Keycloak's admin services when Fine-Grained Admin Permissions (FGAP) v2 is enabled. This issue allows a delegated administrator, who should only have limited control over specific clients, to attach or remove hidden client scopes that they are not authorized to see or manage. As a result, an attacker could inject unauthorized data or permissions into the security tokens issued to end-users, potentially tricking other applications into granting higher levels of access than intended.

## References
- https://access.redhat.com/errata/RHSA-2026:50846
- https://access.redhat.com/errata/RHSA-2026:50847
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/security/cve/CVE-2026-14614
- https://bugzilla.redhat.com/show_bug.cgi?id=2496889
- https://nvd.nist.gov/vuln/detail/CVE-2026-14614
