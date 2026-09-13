# [M] OrientDB Studio web management interface is vulnerable to clickjacking attacks

## Summary
Severity: Medium
Advisory: GHSA-g4gg-9f62-jfph
CVE: CVE-2015-2918
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-g4gg-9f62-jfph
Type: github-advisory

## Affected
- Maven: `com.orientechnologies:orientdb-studio` — affected >=0 <2.0.15
- Maven: `com.orientechnologies:orientdb-studio` — affected >=2.1.0 <2.1.1

## Details
The Studio component in OrientDB Server Community Edition before 2.0.15 and 2.1.x before 2.1.1 does not properly restrict use of FRAME elements, which makes it easier for remote attackers to conduct clickjacking attacks via a crafted web site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2918
- https://github.com/advisories/GHSA-g4gg-9f62-jfph
- https://www.kb.cert.org/vuls/id/845332
