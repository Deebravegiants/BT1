# [M] Keycloak-services: keycloak-services: authenticator config endpoint exposes raw recaptcha secrets to view-only admins

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-16104
Aliases: CVE-2026-16104
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16104
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
A flaw was found in the authentication configuration endpoint of the keycloak-services component, which is the core engine for Red Hat Build of Keycloak identity and access management. The issue occurs because the system fails to mask sensitive configuration values, such as reCAPTCHA secret keys, when they are requested by administrators with view-only permissions. This can lead to the exposure of third-party service credentials to unauthorized personnel or through administrative logs.

## References
- https://access.redhat.com/security/cve/CVE-2026-16104
- https://bugzilla.redhat.com/show_bug.cgi?id=2501737
- https://nvd.nist.gov/vuln/detail/CVE-2026-16104
