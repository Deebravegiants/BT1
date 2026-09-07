# [M] Keycloak services allows the issuance of access and refresh tokens for disabled users

## Summary
Severity: Medium
Advisory: GHSA-wv3h-x6c4-r867
CVE: CVE-2025-14559
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-wv3h-x6c4-r867
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=26.5.0 <26.5.2
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.4.9

## Details
A flaw was found in the keycloak-services component of Keycloak. This vulnerability allows the issuance of access and refresh tokens for disabled users, leading to unauthorized use of previously revoked privileges, via a business logic vulnerability in the Token Exchange implementation when a privileged client invokes the token exchange flow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14559
- https://github.com/keycloak/keycloak/issues/45651
- https://github.com/keycloak/keycloak/commit/2d0aa31c4830ebaad094c3762e78b884c141e659
- https://github.com/keycloak/keycloak/commit/d67349f3aa9fed5c61750619d0f9de6356aeaeff
- https://access.redhat.com/errata/RHSA-2026:2365
- https://access.redhat.com/errata/RHSA-2026:2366
- https://access.redhat.com/security/cve/CVE-2025-14559
- https://bugzilla.redhat.com/show_bug.cgi?id=2421711
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.5.2
