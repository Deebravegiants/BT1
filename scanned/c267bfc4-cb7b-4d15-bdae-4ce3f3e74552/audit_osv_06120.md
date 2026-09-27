# [M] Keycloak-services: keycloak-services: authorization codes can be retargeted to another client session

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-16089
Aliases: CVE-2026-16089
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16089
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
A flaw was found in the keycloak-services component of Red Hat Build of Keycloak. The issue occurs because OAuth 2.0 authorization codes are not properly bound to the client that originally requested them. An attacker who can intercept an authorization code can modify it to be redeemed by their own client, potentially allowing them to obtain access tokens for a victim's identity.

## References
- https://access.redhat.com/security/cve/CVE-2026-16089
- https://bugzilla.redhat.com/show_bug.cgi?id=2501724
- https://nvd.nist.gov/vuln/detail/CVE-2026-16089
