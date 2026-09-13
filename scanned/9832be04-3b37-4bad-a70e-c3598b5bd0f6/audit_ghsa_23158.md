# [H] Improper Privilege Management in Neo4j Graph Database

## Summary
Severity: High
Advisory: GHSA-2w4h-f44w-968f
CVE: CVE-2021-34802
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2w4h-f44w-968f
Type: github-advisory

## Affected
- Maven: `org.neo4j:neo4j-kernel` — affected >=4.2.0 <4.2.8

## Details
A failure in resetting the security context in some transaction actions in Neo4j Graph Database 4.2 could allow authenticated users to execute commands with elevated privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34802
- https://github.com/neo4j/neo4j
- https://neo4j.com
- https://neo4j.com/developer/kb/neo4j-4-2-x-sec-vuln-fix
