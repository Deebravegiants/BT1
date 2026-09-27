# [H] Keycloak-services: keycloak-services: google external access-token exchange bypasses hosted-domain restriction

## Summary
Severity: High
Advisory: BIT-keycloak-2026-18214
Aliases: CVE-2026-18214
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-18214
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
Keycloak allows users to log in using Google accounts and can be configured to only allow users from specific Google Workspace domains. A flaw was found where the token exchange feature, which allows swapping a Google token for a Keycloak token, does not check these domain restrictions. This means an attacker with a valid Google account from a different domain could bypass the security check and gain access to the Keycloak realm.

## References
- https://access.redhat.com/security/cve/CVE-2026-18214
- https://bugzilla.redhat.com/show_bug.cgi?id=2508308
- https://nvd.nist.gov/vuln/detail/CVE-2026-18214
