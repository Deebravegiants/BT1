# [H] Apache Camel-Langchain4j-Tools: Tool argument headers are not filtered against declared parameters

## Summary
Severity: High
Advisory: GHSA-hh8r-75r6-qrg9
CVE: CVE-2026-49042
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-hh8r-75r6-qrg9
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-langchain4j-tools` — affected >=4.8.0 <4.18.3
- Maven: `org.apache.camel:camel-langchain4j-tools` — affected >=4.19.0 <4.21.0
- Maven: `org.apache.camel:camel-langchain4j-agent` — affected >=4.8.0 <4.18.3
- Maven: `org.apache.camel:camel-langchain4j-agent` — affected >=4.19.0 <4.21.0
- Maven: `org.apache.camel:camel-spring-ai-tools` — affected >=4.8.0 <4.18.3
- Maven: `org.apache.camel:camel-spring-ai-tools` — affected >=4.19.0 <4.21.0

## Details
Improper Input Validation vulnerability in Apache Camel.

This issue affects Apache Camel: from 4.8.0 through 4.18.2, from 4.19.0 through 4.20.0.

Users are recommended to upgrade to version 4.18.3, 4.21.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49042
- https://github.com/apache/camel/pull/23535
- https://github.com/apache/camel/pull/23551
- https://github.com/apache/camel/commit/5d0028f6bc7a70556dc1d408b1b6cadb59e1842d
- https://github.com/apache/camel/commit/6851a94075b82375381a7236e081292b67f6bf9a
- https://github.com/apache/camel/commit/e9c4541a91ce75ce4817d499e704299c3933edaa
- https://camel.apache.org/security/CVE-2026-49042.html
- https://github.com/apache/camel
- https://github.com/apache/camel/releases/tag/camel-4.18.3
- https://github.com/apache/camel/releases/tag/camel-4.21.0
- https://issues.apache.org/jira/browse/CAMEL-23621
- http://www.openwall.com/lists/oss-security/2026/07/06/17
