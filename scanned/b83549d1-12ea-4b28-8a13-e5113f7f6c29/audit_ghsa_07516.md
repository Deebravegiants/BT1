# [H] Keycloak: Unauthorized access via improper validation of encrypted SAML assertions

## Summary
Severity: High
Advisory: GHSA-794g-x443-36f7
CVE: CVE-2026-2092
CWE: CWE-1287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-794g-x443-36f7
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0
- Maven: `org.keycloak:keycloak-services` — affected >=26.3.0
- Maven: `org.keycloak:keycloak-services` — affected >=26.5.0

## Details
Keycloak's SAML broker endpoint does not properly validate encrypted assertions when the overall SAML response is not signed. An attacker with a valid signed SAML assertion can exploit this by crafting a malicious SAML response, injecting an encrypted assertion for an arbitrary principal, leading to unauthorized access and potential information disclosure.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-794g-x443-36f7
- https://nvd.nist.gov/vuln/detail/CVE-2026-2092
- https://github.com/keycloak/keycloak/pull/46929
- https://github.com/keycloak/keycloak/commit/b40a25908d937bb0563ea516487bc2c7c1d92508
- https://access.redhat.com/errata/RHSA-2026:3925
- https://access.redhat.com/errata/RHSA-2026:3926
- https://access.redhat.com/errata/RHSA-2026:3947
- https://access.redhat.com/errata/RHSA-2026:3948
- https://access.redhat.com/security/cve/CVE-2026-2092
- https://bugzilla.redhat.com/show_bug.cgi?id=2437296
- https://github.com/keycloak/keycloak
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-2092.json
