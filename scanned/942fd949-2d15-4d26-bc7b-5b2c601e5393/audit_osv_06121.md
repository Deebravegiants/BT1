# [H] Org.keycloak/keycloak-quarkus-server: keycloak: unauthorized access via jwt authorization grant with disabled users

## Summary
Severity: High
Advisory: BIT-keycloak-2026-1609
Aliases: CVE-2026-1609
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-1609
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.5.2 <26.5.3

## Details
A flaw was found in Keycloak. When the JSON Web Token (JWT) authorization grant preview feature is enabled and a user account is disabled, Keycloak fails to validate the user’s disabled status during JWT authorization grant processing. A remote attacker with low privileges can exploit this improper access control vulnerability by presenting a valid assertion token from an external identity provider to obtain a JWT for a disabled user. This allows unauthorized access to sensitive resources.

## References
- https://access.redhat.com/security/cve/CVE-2026-1609
- https://bugzilla.redhat.com/show_bug.cgi?id=2435257
- https://github.com/keycloak/keycloak/issues/46144
- https://github.com/keycloak/keycloak/releases/tag/26.5.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-1609
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-1609.json
