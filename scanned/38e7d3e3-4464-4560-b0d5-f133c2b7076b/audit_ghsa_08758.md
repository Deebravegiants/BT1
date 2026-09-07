# [M] Keycloak has an Out-of-bounds Read

## Summary
Severity: Medium
Advisory: GHSA-cpf7-j4cf-vqx4
CVE: CVE-2026-9803
CWE: CWE-125
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-cpf7-j4cf-vqx4
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0
- Maven: `org.keycloak:keycloak-services` — affected >=26.5.0 <26.6.3

## Details
A flaw was found in Keycloak's ClientRegistrationAuth component. A remote unauthenticated attacker can exploit this vulnerability by sending a specially crafted POST request with a malformed 'Authorization: Bearer' header to any client registration endpoint. This can lead to an ArrayIndexOutOfBoundsException, causing the server to return an HTTP 500 error and resulting in a Denial of Service (DoS) for the affected service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9803
- https://github.com/keycloak/keycloak/issues/49433
- https://github.com/keycloak/keycloak/pull/49500
- https://github.com/keycloak/keycloak/pull/49617
- https://github.com/keycloak/keycloak/pull/49618
- https://github.com/keycloak/keycloak/commit/2b8692499e907e6205be0bd9c8a4da5d46f6ca30
- https://github.com/keycloak/keycloak/commit/3fc06909cc93eb5c4739a712fa350de625812e04
- https://github.com/keycloak/keycloak/commit/ef06df91d344c7e99fcb82987ef6adb854f30789
- https://access.redhat.com/errata/RHSA-2026:25097
- https://access.redhat.com/errata/RHSA-2026:25098
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/security/cve/CVE-2026-9803
- https://bugzilla.redhat.com/show_bug.cgi?id=2482465
- https://github.com/keycloak/keycloak
