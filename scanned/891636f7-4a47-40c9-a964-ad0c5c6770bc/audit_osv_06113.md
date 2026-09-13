# [M] Keycloak-services: keycloak: fgap v2 parent group children endpoint bypasses per-child view permission filter

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-14615
Aliases: CVE-2026-14615
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-14615
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.5

## Details
A flaw was found in the Fine-Grained Admin Permissions (FGAP) v2 implementation within Keycloak's administrative services. When FGAP v2 is enabled, the system fails to properly filter child groups based on the caller's specific permissions when requested through a parent group. This allows a delegated administrator to view details of child groups they are not authorized to access directly, including group names, paths, and custom attributes.

## References
- https://access.redhat.com/errata/RHSA-2026:50846
- https://access.redhat.com/errata/RHSA-2026:50847
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/security/cve/CVE-2026-14615
- https://bugzilla.redhat.com/show_bug.cgi?id=2496891
- https://nvd.nist.gov/vuln/detail/CVE-2026-14615
