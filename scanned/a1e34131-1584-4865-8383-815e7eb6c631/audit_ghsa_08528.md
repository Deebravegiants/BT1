# [M] Keycloak: Insufficient verification proof scoping enables identity provider account linking attack and account compromise

## Summary
Severity: Medium
Advisory: GHSA-m6qj-3mpp-57v8
CVE: CVE-2026-9087
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-m6qj-3mpp-57v8
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.6.3

## Details
A flaw was found in Keycloak. The cross-session verification proof is keyed only by (local userId,
idpAlias) and is not bound to the upstream identity that was actually verified, so a second upstream account on the same IdP can consume it and get linked to the victim's local account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9087
- https://github.com/keycloak/keycloak/commit/37dabf59d0b5ca3e5b3b272bcd3b2580e67b94dd
- https://access.redhat.com/errata/RHSA-2026:25097
- https://access.redhat.com/errata/RHSA-2026:25098
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/security/cve/CVE-2026-9087
- https://bugzilla.redhat.com/show_bug.cgi?id=2480172
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.6.3
