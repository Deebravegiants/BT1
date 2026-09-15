# [M] Apache Camel camel-neo4j component is vulnerable to cypher injection

## Summary
Severity: Medium
Advisory: GHSA-4jrw-64vr-7g8m
CVE: CVE-2025-66169
CWE: CWE-74, CWE-89, CWE-943
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-14
Source: https://github.com/advisories/GHSA-4jrw-64vr-7g8m
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-neo4j` — affected >=4.10.0 <4.10.8
- Maven: `org.apache.camel:camel-neo4j` — affected >=4.14.0 <4.14.3
- Maven: `org.apache.camel:camel-neo4j` — affected >=4.15.0 <4.17.0

## Details
Cypher Injection vulnerability in Apache Camel camel-neo4j component.

This issue affects Apache Camel: from 4.10.0 before 4.10.8, from 4.14.0 before 4.14.3, from 4.15.0 before 4.17.0

Users are recommended to upgrade to version 4.10.8 for 4.10.x LTS and 4.14.3 for 4.14.x LTS and 4.17.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66169
- https://github.com/apache/camel/pull/20035
- https://github.com/apache/camel/pull/20036
- https://github.com/apache/camel/pull/20037
- https://github.com/apache/camel/commit/66715d3feb4ba15df30cffe437e45efeedfba10d
- https://github.com/apache/camel/commit/723e2cd98ce4b4ceb1dd38837bc113fca0cef170
- https://github.com/apache/camel/commit/e46c4c0ef542a64dc791253763a8273dfd7fb179
- https://camel.apache.org/security/CVE-2025-66169.html
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-22719
- http://www.openwall.com/lists/oss-security/2026/01/13/5
