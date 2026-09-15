# [C] Keycloak-services: keycloak-services: saml broker metadata import disables response signature validation

## Summary
Severity: Critical
Advisory: BIT-keycloak-2026-16443
Aliases: CVE-2026-16443
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16443
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.5

## Details
A flaw was found in the SAML metadata import functionality of the keycloak-services component, which is the core engine for identity brokering in Red Hat Build of Keycloak. When importing identity provider metadata that lacks specific usage attributes for keys, the system incorrectly disables signature validation for SAML responses even if a signing certificate is provided. This issue allows an unauthenticated attacker to forge a SAML response and gain unauthorized access to a user account by knowing their external identifier.

## References
- https://access.redhat.com/errata/RHSA-2026:50846
- https://access.redhat.com/errata/RHSA-2026:50847
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/security/cve/CVE-2026-16443
- https://bugzilla.redhat.com/show_bug.cgi?id=2503139
- https://nvd.nist.gov/vuln/detail/CVE-2026-16443
