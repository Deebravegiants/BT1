# [M] Keycloak discloses information without authentication

## Summary
Severity: Medium
Advisory: GHSA-pcv5-m2wh-66j3
CVE: CVE-2020-27838
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pcv5-m2wh-66j3
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <13.0.0

## Details
A flaw was found in keycloak in versions prior to 13.0.0. The client registration endpoint allows fetching information about PUBLIC clients (like client secret) without authentication which could be an issue if the same PUBLIC client changed to CONFIDENTIAL later. The highest threat from this vulnerability is to data confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27838
- https://github.com/keycloak/keycloak/pull/7790
- https://github.com/keycloak/keycloak/commit/9356843c6c3d7097d010b3bb6f91e25fcaba378c
- https://bugzilla.redhat.com/show_bug.cgi?id=1906797
