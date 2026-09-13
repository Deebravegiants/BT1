# [M] Denial of Service in Keycloak Server via Security Headers

## Summary
Severity: Medium
Advisory: GHSA-w3g8-r9gw-qrh8
CVE: CVE-2024-11734
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-01-13
Source: https://github.com/advisories/GHSA-w3g8-r9gw-qrh8
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-quarkus-server` — affected >=0 <26.0.8

## Details
A potential Denial of Service (DoS) vulnerability has been identified in Keycloak, which could allow an administrative user with the rights to change realm settings to disrupt the service. This is done by modifying any of the security headers and inserting newlines, which causes the Keycloak server to write to a request that is already terminated, leading to a failure of said request.

Service disruption may happen, users will be unable to access applications relying on Keycloak, or any of the consoles provided by Keycloak itself on the affected realm.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-w3g8-r9gw-qrh8
- https://nvd.nist.gov/vuln/detail/CVE-2024-11734
- https://github.com/keycloak/keycloak/commit/93b2a7327b2557eb132a8169086c5e63c81dff79
- https://access.redhat.com/errata/RHSA-2025:0299
- https://access.redhat.com/errata/RHSA-2025:0300
- https://access.redhat.com/security/cve/CVE-2024-11734
- https://bugzilla.redhat.com/show_bug.cgi?id=2328846
- https://github.com/keycloak/keycloak
