# [M] Keycloak: Information disclosure via OIDC token introspection endpoint audience bypass

## Summary
Severity: Medium
Advisory: GHSA-4x37-hw65-52w8
CVE: CVE-2026-37979
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-4x37-hw65-52w8
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.6.2

## Details
A flaw was found in Keycloak. This access control vulnerability in Keycloak's OpenID Connect (OIDC) token introspection endpoint allows a confidential client to bypass audience restrictions. An attacker-controlled client with valid credentials can retrieve sensitive token claims intended for other resource servers, compromising the confidentiality of lightweight access tokens. This issue can be exploited remotely by any confidential client in the realm with valid credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-37979
- https://github.com/keycloak/keycloak/issues/49113
- https://access.redhat.com/errata/RHSA-2026:19596
- https://access.redhat.com/errata/RHSA-2026:19597
- https://access.redhat.com/security/cve/CVE-2026-37979
- https://bugzilla.redhat.com/show_bug.cgi?id=2455328
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.6.2
