# [M] CVE-2023-23926

## Summary
Severity: Medium
Advisory: CVE-2023-23926
Aliases: GHSA-6wxg-wh7f-rqpr
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2023-02-16
Source: https://osv.dev/vulnerability/CVE-2023-23926
Type: osv

## Details
APOC (Awesome Procedures on Cypher) is an add-on library for Neo4j. An XML External Entity (XXE) vulnerability found in the apoc.import.graphml procedure of APOC core plugin prior to version 5.5.0 and 4.4.0.14 (4.4 branch) in Neo4j graph database. XML External Entity (XXE) injection occurs when the XML parser allows external entities to be resolved. The XML parser used by the apoc.import.graphml procedure was not configured in a secure way and therefore allowed this. External entities can be used to read local files, send HTTP requests, and perform denial-of-service attacks on the application. Abusing the XXE vulnerability enabled assessors to read local files remotely. Although with the level of privileges assessors had this was limited to one-line files. With the ability to write to the database, any file could have been read. Additionally, assessors noted, with local testing, the server could be crashed by passing in improperly formatted XML. The minimum version containing a patch for this vulnerability is 5.5.0. Those who cannot upgrade the library can control the allowlist of the procedures that can be used in your system.

## References
- https://github.com/neo4j/apoc/releases/tag/5.5.0
- https://neo4j.com/docs/operations-manual/current/reference/configuration-settings/#config_dbms.security.procedures.allowlist
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23926.json
- https://github.com/neo4j/apoc/security/advisories/GHSA-6wxg-wh7f-rqpr
- https://nvd.nist.gov/vuln/detail/CVE-2023-23926
- https://github.com/neo4j/apoc/pull/310
