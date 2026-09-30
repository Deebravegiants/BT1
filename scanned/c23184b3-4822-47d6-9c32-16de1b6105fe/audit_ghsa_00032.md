# [C] XML External Entity (XXE) vulnerability in neo4j.procedure:apoc

## Summary
Severity: Critical
Advisory: GHSA-r2pp-x4mm-4999
CVE: CVE-2018-1000820
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-r2pp-x4mm-4999
Type: github-advisory

## Affected
- Maven: `org.neo4j.procedure:apoc` — affected >=0 <3.4.0.4

## Details
neo4j-contrib neo4j-apoc-procedures version before commit 45bc09c contains a XML External Entity (XXE) vulnerability in XML Parser that can result in Disclosure of confidential data, denial of service, SSRF, port scanning. This vulnerability appears to have been fixed in after commit 45bc09c.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000820
- https://github.com/neo4j-contrib/neo4j-apoc-procedures/issues/931
- https://0dd.zone/2018/10/27/neo4f-apoc-procedures-XXE
