# [H] Org.keycloak:keycloak-services: keycloak: authentication bypass via jwt algorithm confusion

## Summary
Severity: High
Advisory: BIT-keycloak-2026-11800
Aliases: CVE-2026-11800
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-11800
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.4

## Details
A flaw was found in Keycloak. This JWT algorithm confusion vulnerability in the JWT Authorization Grant flow allows an attacker with valid client credentials to bypass signature verification. By forging an assertion, the attacker can create unauthorized access tokens. This enables the attacker to impersonate any federated user linked to the affected Identity Provider, leading to unauthorized access and potential privilege escalation.

## References
- https://access.redhat.com/errata/RHSA-2026:30083
- https://access.redhat.com/errata/RHSA-2026:30084
- https://access.redhat.com/security/cve/CVE-2026-11800
- https://bugzilla.redhat.com/show_bug.cgi?id=2487006
- https://nvd.nist.gov/vuln/detail/CVE-2026-11800
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-11800.json
