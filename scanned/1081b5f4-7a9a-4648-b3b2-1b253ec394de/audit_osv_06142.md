# [H] Org.keycloak.broker.saml: keycloak saml broker: authentication bypass due to disabled saml client completing idp-initiated login

## Summary
Severity: High
Advisory: BIT-keycloak-2026-3047
Aliases: CVE-2026-3047, GHSA-8cr3-vpxx-92cx
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-3047
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.4.10 <26.5.0

## Details
A flaw was found in org.keycloak.broker.saml. When a disabled Security Assertion Markup Language (SAML) client is configured as an Identity Provider (IdP)-initiated broker landing target, it can still complete the login process and establish a Single Sign-On (SSO) session. This allows a remote attacker to gain unauthorized access to other enabled clients without re-authentication, effectively bypassing security restrictions.

## References
- https://access.redhat.com/errata/RHSA-2026:3925
- https://access.redhat.com/errata/RHSA-2026:3926
- https://access.redhat.com/errata/RHSA-2026:3947
- https://access.redhat.com/errata/RHSA-2026:3948
- https://access.redhat.com/security/cve/CVE-2026-3047
- https://bugzilla.redhat.com/show_bug.cgi?id=2441966
- https://nvd.nist.gov/vuln/detail/CVE-2026-3047
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-3047.json
