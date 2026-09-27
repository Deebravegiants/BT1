# [H] Improper Authentication in Keycloak

## Summary
Severity: High
Advisory: GHSA-gf2j-7qwg-4f5x
CVE: CVE-2018-14637
CWE: CWE-285, CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-gf2j-7qwg-4f5x
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <4.6.0

## Details
The SAML broker consumer endpoint in Keycloak before version 4.6.0.Final ignores expiration conditions on SAML assertions. An attacker can exploit this vulnerability to perform a replay attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14637
- https://github.com/advisories/GHSA-gf2j-7qwg-4f5x
