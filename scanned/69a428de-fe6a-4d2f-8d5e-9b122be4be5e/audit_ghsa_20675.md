# [M] Neo4j Graph apoc plugins Partial Path Traversal Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-78f9-745f-278p
CVE: CVE-2022-37423
CWE: CWE-22
Ecosystem: Maven
Published: 2022-08-12
Source: https://github.com/advisories/GHSA-78f9-745f-278p
Type: github-advisory

## Affected
- Maven: `org.neo4j.procedure:apoc` — affected >=4.4.0.0 <4.4.0.8
- Maven: `org.neo4j.procedure:apoc` — affected >=0 <4.3.0.7

## Details
### Impact
A partial Directory Traversal Vulnerability found in `apoc.log.stream` function of apoc plugins in Neo4j Graph database. 
This issue allows a malicious actor to potentially break out of the expected directory. The impact is limited to sibling directories. For example, `userControlled.getCanonicalPath().startsWith("/usr/out")` will allow an attacker to access a directory with a name like `/usr/outnot`.

### Patches
The users should aim to use the latest released version compatible with their Neo4j version. The minimum versions containing patch for this vulnerability are 4.4.0.8 and 4.3.0.7

### Workarounds
If you cannot upgrade the library, you can control the [allowlist of the functions](https://neo4j.com/docs/operations-manual/current/reference/configuration-settings/#config_dbms.security.procedures.allowlist) that can be used in your system


### For more information
If you have any questions or comments about this advisory:
- Open an issue in [neo4j-apoc-procedures](https://github.com/neo4j-contrib/neo4j-apoc-procedures)
- Email us at [security@neo4j.com](mailto:security@neo4j.com)

### Credits
We want to publicly recognise the contribution of [Jonathan Leitschuh](https://github.com/JLLeitschuh) for reporting this issue.

## References
- https://github.com/neo4j-contrib/neo4j-apoc-procedures/security/advisories/GHSA-78f9-745f-278p
- https://nvd.nist.gov/vuln/detail/CVE-2022-37423
- https://github.com/neo4j-contrib/neo4j-apoc-procedures/pull/3080
- https://github.com/neo4j-contrib/neo4j-apoc-procedures/commit/d2f415c6f703bbc2cda4a753928821ff15d5c620
- https://github.com/neo4j-contrib/neo4j-apoc-procedures/commit/fe9f8c77269f5a742585c1d62324eb70755de510
- https://github.com/neo4j-contrib/neo4j-apoc-procedures
- https://neo4j.com/docs/aura/platform/apoc
