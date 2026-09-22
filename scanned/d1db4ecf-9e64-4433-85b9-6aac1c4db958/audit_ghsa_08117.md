# [M] Neo4j Enterprise and Community vulnerable to a potential information disclosure

## Summary
Severity: Medium
Advisory: GHSA-4j3g-rwwq-4p54
CVE: CVE-2026-1622
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-4j3g-rwwq-4p54
Type: github-advisory

## Affected
- Maven: `org.neo4j:neo4j` — affected >=0 <5.26.21
- Maven: `org.neo4j:neo4j` — affected >=2025.01.0 <2026.01.3

## Details
Neo4j Enterprise and Community editions versions prior to 2026.01.3 and 5.26.21 are vulnerable to a potential information disclosure by a user who has ability to access the local log files.

The "obfuscate_literals" option in the query logs does not redact error information, exposing unredacted data in the query log when a customer writes a query that fails. It can allow a user with legitimate access to the local log files to obtain information they are not authorised to see. If this user is also in a position to run queries and trigger errors, this vulnerability can potentially help them to infer information they are not authorised to see through their intended database access.

Neo4j recommends upgrading to versions 2026.01.3 (or 5.26.21) where the issue is fixed, and reviewing query log files permissions to ensure restricted access. If a project's configuration had db.logs.query.obfuscate_literals enabled, and users wish for the obfuscation to cover the error messages as well, theyneed to enable the new configuration setting db.logs.query.obfuscate_errors once they have upgraded Neo4j.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1622
- https://github.com/neo4j/neo4j
- https://neo4j.com/security/CVE-2026-1622
