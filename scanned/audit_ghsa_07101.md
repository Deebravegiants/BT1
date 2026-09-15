# [H] Apache Camel-Neo4j: JSON property names from the CamelNeo4jMatchProperties header are interpolated into the Cypher WHERE clause without validation, allowing Cypher injection (incomplete remediation of CVE-2025-66169)

## Summary
Severity: High
Advisory: GHSA-q86m-qjpm-vqcw
CVE: CVE-2026-46591
CWE: CWE-943
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-q86m-qjpm-vqcw
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-neo4j` — affected >=4.10.0 <4.14.8
- Maven: `org.apache.camel:camel-neo4j` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-neo4j` — affected >=4.19.0 <4.21.0

## Details
Improper Neutralization of Special Elements in Data Query Logic vulnerability in Apache Camel Neo4j component.

The camel-neo4j producer builds the Cypher WHERE clause for its match/retrieve and delete operations from the CamelNeo4jMatchProperties map. CVE-2025-66169 addressed Cypher injection through the property values by binding them as query parameters ($paramN), but the property names (the JSON keys of that map) were still concatenated into the query string verbatim in Neo4jProducer.retrieveNodes() and deleteNode(). A property name containing Cypher syntax therefore alters the structure of the executed query. Where a route maps untrusted input into the CamelNeo4jMatchProperties map - for example by passing a request body as the match map, or from a consumer that does not filter inbound Camel* headers - an attacker who controls the JSON key names can inject arbitrary Cypher and read, modify or delete any node or relationship in the Neo4j database. The CamelNeo4jMatchProperties header is itself Camel-prefixed and is filtered by the HTTP header-filter strategy, so a plain HTTP client cannot set it directly; the issue is reachable through routes that deliberately or inadvertently carry untrusted data into that header.
This issue affects Apache Camel: from 4.10.0 before 4.14.8, from 4.15.0 before 4.18.3, from 4.19.0 before 4.21.0.

Users are recommended to upgrade to version 4.21.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.8. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.3. For deployments that cannot upgrade immediately, do not populate the CamelNeo4jMatchProperties map from untrusted input: validate or allow-list the property names (for example against ^[A-Za-z_][A-Za-z0-9_]*$) before the Neo4j producer, and ensure that any consumer feeding such a route filters inbound Camel* / camel* headers so the match header cannot be supplied by an external sender.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46591
- https://github.com/apache/camel/pull/23258
- https://github.com/apache/camel/pull/23294
- https://github.com/apache/camel/pull/23323
- https://github.com/apache/camel/commit/7881d949c40befcc602016dcce25a2fb38d070ce
- https://github.com/apache/camel/commit/865d0b8b99f969e06ec6275b69c72670b5763245
- https://github.com/apache/camel/commit/bb4176fe87dc0cc60a5be37a57b69b8c610c1dd2
- https://camel.apache.org/security/CVE-2026-46591.html
- https://github.com/advisories/GHSA-4jrw-64vr-7g8m
- https://github.com/apache/camel
- https://github.com/apache/camel/releases/tag/camel-4.14.8
- https://github.com/apache/camel/releases/tag/camel-4.18.3
- https://github.com/apache/camel/releases/tag/camel-4.21.0
- https://issues.apache.org/jira/browse/CAMEL-23528
