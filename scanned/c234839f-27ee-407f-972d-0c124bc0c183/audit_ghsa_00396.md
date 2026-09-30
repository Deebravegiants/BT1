# [M] keycloak-core discloses system properties

## Summary
Severity: Medium
Advisory: GHSA-c77r-6f64-478q
CVE: CVE-2017-2582
CWE: CWE-200, CWE-201
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-c77r-6f64-478q
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <2.5.1

## Details
It was found that while parsing the SAML messages the StaxParserUtil class of keycloak before 2.5.1 replaces special strings for obtaining attribute values with system property. This could allow an attacker to determine values of system properties at the attacked system by formatting the SAML request ID field to be the chosen system property which could be obtained in the "InResponseTo" field in the response.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2582
- https://github.com/advisories/GHSA-c77r-6f64-478q
