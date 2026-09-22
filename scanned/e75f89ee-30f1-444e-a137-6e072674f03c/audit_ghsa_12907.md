# [H] org.neo4j.procedure:apoc Path Traversal Vulnerability

## Summary
Severity: High
Advisory: GHSA-5v8v-gwmw-qw97
CVE: CVE-2022-23532
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2023-01-13
Source: https://github.com/advisories/GHSA-5v8v-gwmw-qw97
Type: github-advisory

## Affected
- Maven: `org.neo4j.procedure:apoc` — affected >=0 <4.3.0.12
- Maven: `org.neo4j.procedure:apoc` — affected >=4.4.0.0 <4.4.0.12

## Details
### Impact
A Path Traversal Vulnerability found in the apoc.export.* procedures of apoc plugins in Neo4j Graph database.
The issue allows a malicious actor to potentially break out of the expected directory. The vulnerability is such that files could only be created but not overwritten.

For the vulnerability to be exploited, an attacker would need access to execute an arbitrary query, either by having access to an authenticated Neo4j client, or a Cypher injection vulnerability in an application. The procedure would need to have been allow listed in the neo4j configuration as well as having the apoc config `apoc.export.file.enabled` set to true. 

On a UNIX based system the following query allows arbitrary write access to the tmp folder:

CALL apoc.export.csv.query('RETURN 1', 'file:///..//..//..//..//tmp/test.txt', {})

### Patches
The users should aim to use the latest released version compatible with their Neo4j version. The minimum versions containing patch for this vulnerability are 4.4.0.12 and 4.3.0.12.

### Workarounds
If you cannot upgrade the library, you can control the [allowlist of the ](https://neo4j.com/docs/operations-manual/current/reference/configuration-settings/#config_dbms.security.procedures.allowlist)procedures that can be used in your system, and/or turn off local file access by setting apoc.export.file.enabled=false

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [neo4j-apoc-procedures](https://github.com/neo4j-contrib/neo4j-apoc-procedures)
* Email us at [security@neo4j.com](mailto:security@neo4j.com)

### Credits
We want to publicly recognise the contribution Adam Reziouk - Airbus.

## References
- https://github.com/neo4j-contrib/neo4j-apoc-procedures/security/advisories/GHSA-5v8v-gwmw-qw97
- https://nvd.nist.gov/vuln/detail/CVE-2022-23532
- https://github.com/neo4j-contrib/neo4j-apoc-procedures/commit/01e63ed2d187cd2a8aa1d78bf831ef0fdd69b522
- https://github.com/neo4j-contrib/neo4j-apoc-procedures
