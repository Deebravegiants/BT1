# [C] Keycloak-services: keycloak-services: saml idp-initiated broker login bypasses link-only restriction

## Summary
Severity: Critical
Advisory: BIT-keycloak-2026-16442
Aliases: CVE-2026-16442
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16442
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.5

## Details
A flaw was found in the SAML broker component of Keycloak, which is used to manage identity federation and user authentication. The issue occurs because the IdP-initiated Single Sign-On endpoint fails to check if a provider is restricted to account linking only. This allows an attacker with control over a linked upstream identity to bypass login restrictions and gain full access to a local user account.

## References
- https://access.redhat.com/errata/RHSA-2026:50846
- https://access.redhat.com/errata/RHSA-2026:50847
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/security/cve/CVE-2026-16442
- https://bugzilla.redhat.com/show_bug.cgi?id=2503138
- https://nvd.nist.gov/vuln/detail/CVE-2026-16442
