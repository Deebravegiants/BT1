# [C] Neo4j Graph Database vulnerable to Path Traversal

## Summary
Severity: Critical
Advisory: GHSA-4mpj-488r-vh6m
CVE: CVE-2021-42767
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-4mpj-488r-vh6m
Type: github-advisory

## Affected
- Maven: `org.neo4j.procedure:apoc` — affected >=0 <3.5.17
- Maven: `org.neo4j.procedure:apoc` — affected >=4.2.0 <4.2.10
- Maven: `org.neo4j.procedure:apoc` — affected >=4.3.0.0 <4.3.0.4
- Maven: `org.neo4j.procedure:apoc` — affected >=4.4.0.0 <4.4.0.1

## Details
### Impact
Directory Traversal Vulnerabilities found in several functions of apoc plugins in Neo4j Graph database. The attacker can retrieve and download files from outside the configured directory on the affected server. Under some circumstances, the attacker can also create files.

### Patches
The users should aim to use the latest released version compatible with their Neo4j version. The minimum versions containing patch for this vulnerability (for Neo4j 4.2, 4.3, and 4.4 bundled with APOC, upgrade to the appropriate patched version):
3.5 - bundle n/a, standalone 3.5.0.17
4.2 - bundle 4.2.13, standalone 4.2.0.10
4.3 - bundle 4.3.9, standalone 4.3.0.4
4.4 - bundle 4.4.2, standalone 4.4.0.1

### Workarounds
If you cannot upgrade the library, you can control the [allowlist of the functions](https://neo4j.com/docs/operations-manual/current/reference/configuration-settings/#config_dbms.security.procedures.allowlist) that can be used in your system:


### For more information
If you have any questions or comments about this advisory:
* Open an issue in [neo4j-apoc-procedures](https://github.com/neo4j-contrib/neo4j-apoc-procedures)
* Email us at [security@neo4j.com](mailto:security@neo4j.com)

### Credits
We want to publicly recognize the contribution of Nicolai Grødum from the Red Team of PwC Norway for reporting this issue and following the responsible disclosure [policy](https://neo4j.com/trust-center/responsible-disclosure/).

## References
- https://github.com/neo4j-contrib/neo4j-apoc-procedures/security/advisories/GHSA-4mpj-488r-vh6m
- https://nvd.nist.gov/vuln/detail/CVE-2021-42767
- https://neo4j.com
