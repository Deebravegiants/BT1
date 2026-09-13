# [H] Keycloak-services: keycloak-services: authorization bypass via unnormalized uri matching in pathmatcher

## Summary
Severity: High
Advisory: BIT-keycloak-2026-15573
Aliases: CVE-2026-15573
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-15573
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.5

## Details
A flaw was found in Keycloak's Authorization Services. The component responsible for matching request paths to security policies (PathMatcher) does not properly normalize URIs before comparison. By adding extra characters like a trailing slash or matrix parameters to a URL, an attacker can trick the system into applying a less restrictive security policy than intended. This allows an authenticated user to access administrative or restricted areas they should not have permission to see.

## References
- https://access.redhat.com/errata/RHSA-2026:50846
- https://access.redhat.com/errata/RHSA-2026:50847
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/security/cve/CVE-2026-15573
- https://bugzilla.redhat.com/show_bug.cgi?id=2499593
- https://nvd.nist.gov/vuln/detail/CVE-2026-15573
