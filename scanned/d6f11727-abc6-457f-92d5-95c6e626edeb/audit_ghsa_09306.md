# [M] Keycloak Vulnerable to Incorrect Authorization

## Summary
Severity: Medium
Advisory: GHSA-4q93-v92x-p89f
CVE: CVE-2026-9791
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-4q93-v92x-p89f
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-server-spi-private` — affected >=26.5.0 <26.6.3
- Maven: `org.keycloak:keycloak-services` — affected >=26.5.0 <26.6.3
- Maven: `org.keycloak:keycloak-server-spi-private` — affected >=0
- Maven: `org.keycloak:keycloak-services` — affected >=0

## Details
A flaw was found in Keycloak. An authenticated user with existing organization membership can exploit this flaw by accessing user-facing APIs, such as the account API or by requesting an OpenID Connect (OIDC) token with the 'organization' scope. This allows organization metadata to be disclosed in tokens, even after an administrator has explicitly disabled the Organizations feature, potentially leading to incorrect authorization decisions by resource servers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9791
- https://github.com/keycloak/keycloak/issues/49431
- https://github.com/keycloak/keycloak/pull/49541
- https://github.com/keycloak/keycloak/pull/49678
- https://github.com/keycloak/keycloak/pull/49680
- https://github.com/keycloak/keycloak/commit/0e706e7c83d1e971b48656ad9e674eec6adc225b
- https://github.com/keycloak/keycloak/commit/a77c60f2f3e0793046add44120579871e92553df
- https://github.com/keycloak/keycloak/commit/f19e1f2b4e998116d4e321f50ecf99c0f87b862f
- https://access.redhat.com/errata/RHSA-2026:25097
- https://access.redhat.com/errata/RHSA-2026:25098
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/security/cve/CVE-2026-9791
- https://bugzilla.redhat.com/show_bug.cgi?id=2482458
- https://github.com/keycloak/keycloak
