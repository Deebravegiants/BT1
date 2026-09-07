# [M] Reflected XSS on clients-registrations endpoint

## Summary
Severity: Medium
Advisory: GHSA-m98g-63qj-fp8j
CWE: CWE-79
Ecosystem: Maven
Published: 2022-04-28
Source: https://github.com/advisories/GHSA-m98g-63qj-fp8j
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=10.0.0 <18.0.0

## Details
A POST based reflected Cross Site Scripting vulnerability on has been identified in Keycloak. When a malicious request is sent to the client registration endpoint, the error message is not properly escaped, allowing an attacker to execute malicious scripts into the user's browser.

### Acknowledgement

Keycloak would like to thank Quentin TEXIER (Pentester at Opencyber) for reporting this issue.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-m98g-63qj-fp8j
- https://github.com/keycloak/keycloak
