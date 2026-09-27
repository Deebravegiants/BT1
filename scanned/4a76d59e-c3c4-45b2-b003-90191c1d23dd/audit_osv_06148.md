# [H] Keycloak-policy-enforcer: keycloak policy enforcer: authorization bypass via incorrect uri comparison

## Summary
Severity: High
Advisory: BIT-keycloak-2026-9800
Aliases: CVE-2026-9800
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-9800
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.7.0

## Details
A flaw was found in Keycloak Policy Enforcer. This vulnerability allows any authenticated user to bypass all authorization policies, including role, scope, and User-Managed Access (UMA) permission checks. By including the configured access-denied page path within a request URL, either as a path segment or a query parameter, an attacker can gain unauthorized access to protected resources.

## References
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/errata/RHSA-2026:30083
- https://access.redhat.com/errata/RHSA-2026:30084
- https://access.redhat.com/errata/RHSA-2026:50846
- https://access.redhat.com/errata/RHSA-2026:50847
- https://access.redhat.com/security/cve/CVE-2026-9800
- https://bugzilla.redhat.com/show_bug.cgi?id=2482472
- https://nvd.nist.gov/vuln/detail/CVE-2026-9800
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-9800.json
