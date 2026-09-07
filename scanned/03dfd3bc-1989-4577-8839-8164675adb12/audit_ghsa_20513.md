# [H] Improper Authorization in Keycloak

## Summary
Severity: High
Advisory: GHSA-83x4-9cwr-5487
CVE: CVE-2021-4133
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-83x4-9cwr-5487
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <15.1.1

## Details
A incorrect authorization flaw was found in Keycloak 12.0.0, the flaw allows an attacker with any existing user account to create new default user accounts via the administrative REST API even where new user registration is disabled.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-83x4-9cwr-5487
- https://nvd.nist.gov/vuln/detail/CVE-2021-4133
- https://github.com/keycloak/keycloak/issues/9247
- https://bugzilla.redhat.com/show_bug.cgi?id=2033602
- https://github.com/keycloak/keycloak
- https://www.oracle.com/security-alerts/cpuapr2022.html
