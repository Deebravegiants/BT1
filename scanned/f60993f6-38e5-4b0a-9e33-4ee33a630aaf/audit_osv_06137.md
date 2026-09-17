# [M] Keycloak-services: keycloak-services: client not-before revocation ignored when realm not-before is older but nonzero

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-18218
Aliases: CVE-2026-18218
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-18218
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
A flaw was found in the TokenManager component of the Keycloak identity management service. When an administrator attempts to revoke tokens for a specific application (client) using a "not-before" policy, the revocation may be silently ignored if the overall security realm already has an older, non-zero revocation policy in place. This issue can allow previously issued tokens to remain valid for refreshing sessions and accessing user information even after an administrator has attempted to invalidate them.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## References
- https://access.redhat.com/security/cve/CVE-2026-18218
- https://bugzilla.redhat.com/show_bug.cgi?id=2508313
- https://nvd.nist.gov/vuln/detail/CVE-2026-18218
