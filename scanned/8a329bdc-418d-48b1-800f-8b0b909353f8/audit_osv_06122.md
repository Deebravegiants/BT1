# [M] Keycloak-services: keycloak-services: required signed-jwt assertion policy can be bypassed with unsigned assertion headers

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-16093
Aliases: CVE-2026-16093
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16093
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
Keycloak provides a mechanism called Client Policies to enforce security requirements on clients, such as requiring them to use signed JWTs for authentication. A flaw was discovered where this enforcement can be bypassed. An attacker with valid client credentials can provide a fake, unsigned assertion header that tricks the system into thinking the policy requirements have been met. This allows the attacker to authenticate using simpler methods like a client secret even when the administrator has mandated more secure, signed assertions.

## References
- https://access.redhat.com/security/cve/CVE-2026-16093
- https://bugzilla.redhat.com/show_bug.cgi?id=2501729
- https://nvd.nist.gov/vuln/detail/CVE-2026-16093
