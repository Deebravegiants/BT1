# [M] XML External Entity (XXE) vulnerability in apoc.import.graphml

## Summary
Severity: Medium
Advisory: GHSA-9vx8-f5c4-862x
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2023-02-24
Source: https://github.com/advisories/GHSA-9vx8-f5c4-862x
Type: github-advisory

## Affected
- Maven: `org.neo4j.procedure:apoc` — affected >=0 <4.4.0.14
- Maven: `org.neo4j.procedure:apoc` — affected >=5.0.0 <5.5.0

## Details
### Impact
A XML External Entity (XXE) vulnerability found in the apoc.import.graphml procedure of APOC core plugin in Neo4j graph database. XML External Entity (XXE) injection occurs when the XML parser allows external entities to be resolved. The XML parser used by the apoc.import.graphml procedure was not configured in a secure way and therefore allowed this.

External entities can be used to read local files, send HTTP requests, and perform denial-of-service attacks on the application.

Abusing the XXE vulnerability enabled assessors to read local files remotely. Although with the level of privileges assessors had this was limited to one-line files. With the ability to write to the database, any file could have been read. Additionally, assessors noted, with local testing, the server could be crashed by passing in improperly formatted XML. 

### Patches
The users should aim to use the latest released version compatible with their Neo4j version. The minimum versions containing patch for this vulnerability is 4.4.0.14. 

### Workarounds
If you cannot upgrade the library, you can control the [allowlist](https://neo4j.com/docs/operations-manual/current/reference/configuration-settings/#config_dbms.security.procedures.allowlist)  of the  procedures that can be used in your system.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [neo4j-apoc-procedures](https://github.com/neo4j-contrib/neo4j-apoc-procedures)
* Email us at [security@neo4j.com](mailto:security@neo4j.com)

### Credits
We want to publicly recognise the contribution of Christopher Schneider – State Farm.

## References
- https://github.com/neo4j-contrib/neo4j-apoc-procedures/security/advisories/GHSA-9vx8-f5c4-862x
- https://github.com/neo4j/apoc/security/advisories/GHSA-6wxg-wh7f-rqpr
- https://nvd.nist.gov/vuln/detail/CVE-2023-23926
- https://github.com/neo4j-contrib/neo4j-apoc-procedures/commit/c3e2a29020497acf9417879f38e8af4e8c6d5783
- https://github.com/neo4j-contrib/neo4j-apoc-procedures
- https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/tag/4.4.0.14
