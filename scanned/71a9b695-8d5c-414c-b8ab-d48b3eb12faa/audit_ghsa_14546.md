# [H] Keycloak vulnerable to user impersonation via stolen UUID code

## Summary
Severity: High
Advisory: GHSA-9g98-5mj6-f9mv
CVE: CVE-2023-0264
CWE: CWE-287, CWE-345
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-03-02
Source: https://github.com/advisories/GHSA-9g98-5mj6-f9mv
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <21.0.1

## Details
Keycloak's OpenID Connect user authentication was found to incorrectly authenticate requests. An authenticated attacker who could also obtain a certain piece of info from a user request, from a victim within the same realm, could use that data to impersonate the victim and generate new session tokens.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-9g98-5mj6-f9mv
- https://nvd.nist.gov/vuln/detail/CVE-2023-0264
- https://github.com/keycloak/keycloak/commit/ec8109112e67208c13e13f6d1f8706a5a3ba8d4c
- https://access.redhat.com/security/cve/CVE-2023-0264
- https://github.com/keycloak/keycloak
