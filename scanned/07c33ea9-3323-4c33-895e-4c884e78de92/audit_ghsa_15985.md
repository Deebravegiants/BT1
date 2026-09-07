# [H] Keycloak has session fixation in Elytron SAML adapters

## Summary
Severity: High
Advisory: GHSA-5rxp-2rhr-qwqv
CVE: CVE-2024-7341
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-14
Source: https://github.com/advisories/GHSA-5rxp-2rhr-qwqv
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <22.0.12
- Maven: `org.keycloak:keycloak-services` — affected >=23.0.0 <24.0.7
- Maven: `org.keycloak:keycloak-services` — affected >=25.0.0 <25.0.5

## Details
A session fixation issue was discovered in the SAML adapters provided by Keycloak. The session ID and JSESSIONID cookie are not changed at login time, even when the turnOffChangeSessionIdOnLogin option is configured. This flaw allows an attacker who hijacks the current session before authentication to trigger session fixation.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-5rxp-2rhr-qwqv
- https://nvd.nist.gov/vuln/detail/CVE-2024-7341
- https://github.com/keycloak/keycloak/commit/5e06da2f6794c695051605e26a01affa3a18f66b
- https://github.com/keycloak/keycloak/commit/5b3de0c7e7f367103affe2f5167913a2ce021cf1
- https://github.com/keycloak/keycloak/commit/2341d6ee7a3567c58fd6a04a419fe4403e13374c
- https://github.com/keycloak/keycloak
- https://bugzilla.redhat.com/show_bug.cgi?id=2302064
- https://access.redhat.com/security/cve/CVE-2024-7341
- https://access.redhat.com/errata/RHSA-2024:6503
- https://access.redhat.com/errata/RHSA-2024:6502
- https://access.redhat.com/errata/RHSA-2024:6501
- https://access.redhat.com/errata/RHSA-2024:6500
- https://access.redhat.com/errata/RHSA-2024:6499
- https://access.redhat.com/errata/RHSA-2024:6497
- https://access.redhat.com/errata/RHSA-2024:6495
- https://access.redhat.com/errata/RHSA-2024:6494
- https://access.redhat.com/errata/RHSA-2024:6493
