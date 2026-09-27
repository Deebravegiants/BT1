# [M] Keycloak allows unrestricted admin use of system and environment variables

## Summary
Severity: Medium
Advisory: GHSA-f4v7-3mww-9gc2
CVE: CVE-2024-11736
CWE: CWE-526
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-13
Source: https://github.com/advisories/GHSA-f4v7-3mww-9gc2
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-quarkus-server` — affected >=0 <26.0.8

## Details
A security vulnerability has been identified that allows admin users to access sensitive server environment variables and system properties through user-configurable URLs. Specifically, when configuring backchannel logout URLs or admin URLs, admin users can include placeholders like ${env.VARNAME} or ${PROPNAME}. The server replaces these placeholders with the actual values of environment variables or system properties during URL processing.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-f4v7-3mww-9gc2
- https://nvd.nist.gov/vuln/detail/CVE-2024-11736
- https://github.com/keycloak/keycloak/commit/7a76858fe4aa39a39fb6b86dd3d2c113d9c59854
- https://access.redhat.com/errata/RHSA-2025:0299
- https://access.redhat.com/errata/RHSA-2025:0300
- https://access.redhat.com/security/cve/CVE-2024-11736
- https://bugzilla.redhat.com/show_bug.cgi?id=2328850
- https://github.com/keycloak/keycloak
