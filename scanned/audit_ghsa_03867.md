# [M] Use of Cryptographically Weak Pseudo-Random Number Generator in org.pac4j:pac4j-saml

## Summary
Severity: Medium
Advisory: GHSA-rc75-cf5c-mxvh
CVE: CVE-2019-10755
CWE: CWE-338
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-11-06
Source: https://github.com/advisories/GHSA-rc75-cf5c-mxvh
Type: github-advisory

## Affected
- Maven: `org.pac4j:pac4j-saml` — affected >=0 <3.8.2

## Details
The SAML identifier generated within SAML2Utils.java was found to make use of the apache commons-lang3 RandomStringUtils class which makes them predictable due to RandomStringUtils PRNG's algorithm not being cryptographically strong. This issue only affects the 3.X release of pac4j-saml.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10755
- https://github.com/pac4j/pac4j/commit/34d5b1028a2db201ee81ec51b52a782fe073f609
- https://snyk.io/vuln/SNYK-JAVA-ORGPAC4J-467407
