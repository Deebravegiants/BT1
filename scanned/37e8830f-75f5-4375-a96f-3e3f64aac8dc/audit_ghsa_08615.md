# [H] Apache Flink: Remote code execution via SQL injection in code generation

## Summary
Severity: High
Advisory: GHSA-2f54-v4hm-fx73
CVE: CVE-2026-35194
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-2f54-v4hm-fx73
Type: github-advisory

## Affected
- Maven: `org.apache.flink:flink-table-planner_2.12` — affected >=1.15.0 <1.20.4
- Maven: `org.apache.flink:flink-table-planner_2.12` — affected >=2.0.0 <2.0.2
- Maven: `org.apache.flink:flink-table-planner_2.12` — affected >=2.1.0 <2.1.2
- Maven: `org.apache.flink:flink-table-planner_2.12` — affected >=2.2.0 <2.2.1
- Maven: `org.apache.flink:flink-table-api-java` — affected >=1.15.0 <1.20.4
- Maven: `org.apache.flink:flink-table-api-java` — affected >=2.0.0 <2.0.2
- Maven: `org.apache.flink:flink-table-api-java` — affected >=2.1.0 <2.1.2
- Maven: `org.apache.flink:flink-table-api-java` — affected >=2.2.0 <2.2.1
- Maven: `org.apache.flink:flink-table-runtime` — affected >=1.15.0 <1.20.4
- Maven: `org.apache.flink:flink-table-runtime` — affected >=2.0.0 <2.0.2
- Maven: `org.apache.flink:flink-table-runtime` — affected >=2.1.0 <2.1.2
- Maven: `org.apache.flink:flink-table-runtime` — affected >=2.2.0 <2.2.1

## Details
Code injection in SQL code generation in Apache Flink 1.15.0 through 1.20.x and 2.0.0 through 2.x allows authenticated users with query submission privileges to execute arbitrary code on TaskManagers via maliciously crafted SQL queries. The vulnerability affects JSON functions (1.15.0+) and LIKE expressions with ESCAPE clauses (1.17.0+). User-controlled strings are interpolated into generated Java code without proper escaping, allowing attackers to break out of string literals and inject arbitrary expressions.

Users are recommended to upgrade to either version 1.20.4, 2.0.2, 2.1.2 or 2.2.1, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35194
- https://github.com/apache/flink/commit/64007b131d689158af90ca1c1b71b018129a85c5
- https://github.com/apache/flink/commit/8db22cf8fbc4c785f6ffd41c2fd3e8b64a9688cd
- https://github.com/apache/flink
- https://lists.apache.org/thread/qh52bw4hhvy7n2owd8b3bt51mz0lvj9x
- http://www.openwall.com/lists/oss-security/2026/05/15/20
