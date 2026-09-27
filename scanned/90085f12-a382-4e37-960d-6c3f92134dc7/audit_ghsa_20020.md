# [C] Keycloak vulnerable to path traversal via double URL encoding 

## Summary
Severity: Critical
Advisory: GHSA-g8q8-fggx-9r3q
CVE: CVE-2022-3782
CWE: CWE-177, CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-g8q8-fggx-9r3q
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <20.0.2

## Details
Keycloak does not properly validate URLs included in a redirect. An attacker could construct a malicious request to bypass validation and access other URLs and potentially sensitive information within the domain, or possibly conduct further attacks.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-g8q8-fggx-9r3q
- https://nvd.nist.gov/vuln/detail/CVE-2022-3782
- https://github.com/keycloak/keycloak/pull/15982/commits/1987c942f527b9f3bbf2a86ba71ba8ae0154ac37
- https://access.redhat.com/security/cve/CVE-2022-3782
- https://github.com/keycloak/keycloak
