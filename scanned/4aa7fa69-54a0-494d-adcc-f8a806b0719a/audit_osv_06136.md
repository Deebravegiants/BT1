# [H] Keycloak-services: keycloak-services: microsoft external access-token exchange bypasses configured tenant

## Summary
Severity: High
Advisory: BIT-keycloak-2026-18215
Aliases: CVE-2026-18215
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-18215
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
Keycloak provides a way to let users log in using Microsoft accounts while restricting access to a specific organization (tenant). A flaw was discovered where this restriction is ignored when using the token exchange feature. This means an attacker with a valid Microsoft token from a completely different organization could gain access to the Keycloak realm, potentially accessing sensitive data or performing unauthorized actions.

## References
- https://access.redhat.com/security/cve/CVE-2026-18215
- https://bugzilla.redhat.com/show_bug.cgi?id=2508309
- https://nvd.nist.gov/vuln/detail/CVE-2026-18215
