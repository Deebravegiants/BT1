# [M] Keycloak-services: keycloak-services: incorrect authorization in admin role-composite deletion allows delegated admin to remove privileged child roles

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-16106
Aliases: CVE-2026-16106
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16106
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
A flaw was found in the admin REST API of Keycloak, a solution for identity and access management. The issue occurs when a delegated administrator attempts to remove a child role from a composite role. Due to missing authorization checks, an attacker with limited administrative permissions can remove privileged roles they are not authorized to manage, leading to a loss of access for other users and administrators.

## References
- https://access.redhat.com/security/cve/CVE-2026-16106
- https://bugzilla.redhat.com/show_bug.cgi?id=2501739
- https://nvd.nist.gov/vuln/detail/CVE-2026-16106
