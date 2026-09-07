# [M] HTML Injection in Keycloak Admin REST API

## Summary
Severity: Medium
Advisory: GHSA-m4fv-gm5m-4725
CVE: CVE-2022-1274
CWE: CWE-79, CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-01
Source: https://github.com/advisories/GHSA-m4fv-gm5m-4725
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <20.0.5

## Details
The `execute-actions-email` endpoint of the Keycloak Admin REST API allows a malicious actor to send emails containing phishing links to Keycloak users.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-m4fv-gm5m-4725
- https://nvd.nist.gov/vuln/detail/CVE-2022-1274
- https://github.com/keycloak/keycloak/pull/16764
- https://github.com/keycloak/keycloak/commit/fc3c61235fa30132123c17ed8702ff7b3a672fe9
- https://bugzilla.redhat.com/show_bug.cgi?id=2073157
- https://github.com/keycloak/keycloak
- https://herolab.usd.de/security-advisories/usd-2021-0033
