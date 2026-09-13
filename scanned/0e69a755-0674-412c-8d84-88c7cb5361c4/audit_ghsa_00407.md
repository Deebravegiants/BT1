# [H] Keycloak vulnerable to infinite loop based Denial of Service

## Summary
Severity: High
Advisory: GHSA-jc6q-27mw-p55w
CVE: CVE-2017-2646
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-jc6q-27mw-p55w
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <2.5.5

## Details
When Keycloak versions prior to 2.5.5 receive a Logout request with an Extensions in the middle of the request, the SAMLSloRequestParser.parse() method ends in an infinite loop. An attacker could use this flaw to conduct denial of service attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2646
- https://github.com/advisories/GHSA-jc6q-27mw-p55w
- https://github.com/keycloak/keycloak
