# [H] Keycloak-services: keycloak-services: fgap v2 group assignment bypass during user creation

## Summary
Severity: High
Advisory: BIT-keycloak-2026-18571
Aliases: CVE-2026-18571
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-18571
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
A flaw was found in the user creation component of Keycloak when Fine-Grained Admin Permissions V2 (FGAP V2) is enabled. This issue allows a sub-administrator with permission to create users to add those users to any group, even groups the sub-administrator is not authorized to manage. This could lead to unauthorized access to sensitive information or elevated privileges for the newly created users.

## References
- https://access.redhat.com/security/cve/CVE-2026-18571
- https://bugzilla.redhat.com/show_bug.cgi?id=2509759
- https://nvd.nist.gov/vuln/detail/CVE-2026-18571
