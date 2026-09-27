# [M] Keycloak-services: keycloak-services: keycloak: fgap v2 role groups endpoint discloses hidden group metadata without group view permission

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-14613
Aliases: CVE-2026-14613
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-14613
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.2

## Details
A vulnerability was discovered in Keycloak's administrative interface that allows certain administrators to see information about groups they shouldn't have access to. When the new Fine-Grained Admin Permissions (FGAP v2) are turned on, an administrator who is allowed to see a specific "role" can also see a list of all groups assigned to that role. The system fails to check if the administrator has permission to see those specific groups. This could allow a restricted administrator to discover "hidden" groups and see their details, such as internal names and custom settings, which might contain sensitive deployment information.

## References
- https://access.redhat.com/errata/RHSA-2026:56523
- https://access.redhat.com/errata/RHSA-2026:56524
- https://access.redhat.com/security/cve/CVE-2026-14613
- https://bugzilla.redhat.com/show_bug.cgi?id=2496878
- https://nvd.nist.gov/vuln/detail/CVE-2026-14613
