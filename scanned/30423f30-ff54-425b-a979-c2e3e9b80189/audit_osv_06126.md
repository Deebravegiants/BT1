# [M] Keycloak-services: keycloak-services: missing per-role authorization on rolecontainerresource composite endpoints

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-16105
Aliases: CVE-2026-16105
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16105
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
A flaw was found in the RoleContainerResource component of Keycloak. The issue occurs because certain name-based endpoints in the admin REST API do not properly enforce authorization checks when managing composite roles. This allows a delegated administrator with manage-realm permissions to remove essential child roles from built-in admin roles, potentially disrupting administrative functions within a realm.

## References
- https://access.redhat.com/security/cve/CVE-2026-16105
- https://bugzilla.redhat.com/show_bug.cgi?id=2501738
- https://nvd.nist.gov/vuln/detail/CVE-2026-16105
