# [C] Keycloak vulnerable to privilege escalation on Token Exchange feature

## Summary
Severity: Critical
Advisory: GHSA-75p6-52g3-rqc8
CVE: CVE-2022-1245
CWE: CWE-639, CWE-862, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-26
Source: https://github.com/advisories/GHSA-75p6-52g3-rqc8
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <18.0.0

## Details
A privilege escalation flaw was found in the token exchange feature of keycloak. Missing authorization allows a client application holding a valid access token to exchange tokens for any target client by passing the client_id of the target. This could allow a client to gain unauthorized access to additional services.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-75p6-52g3-rqc8
- https://nvd.nist.gov/vuln/detail/CVE-2022-1245
- https://github.com/keycloak/keycloak/commit/76d83f46fad94ebcbedaa49e6daad458e2894e52
- https://github.com/keycloak/keycloak
