# [H] Deserialization of Untrusted Data in Apache Camel CassandraQL

## Summary
Severity: High
Advisory: GHSA-m43p-55rf-8c2j
CVE: CVE-2024-23114
CWE: CWE-502
Ecosystem: Maven
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-m43p-55rf-8c2j
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-cassandraql` — affected >=3.0.0 <3.21.4
- Maven: `org.apache.camel:camel-cassandraql` — affected >=3.22.0 <3.22.1
- Maven: `org.apache.camel:camel-cassandraql` — affected >=4.0.0 <4.0.4
- Maven: `org.apache.camel:camel-cassandraql` — affected >=4.1.0 <4.4.0

## Details
Deserialization of Untrusted Data vulnerability in Apache Camel CassandraQL Component AggregationRepository which is vulnerable to unsafe deserialization. Under specific conditions it is possible to deserialize malicious payload.This issue affects Apache Camel: from 3.0.0 before 3.21.4, from 3.22.0 before 3.22.1, from 4.0.0 before 4.0.4, from 4.1.0 before 4.4.0.

Users are recommended to upgrade to version 4.4.0, which fixes the issue. If users are on the 4.0.x LTS releases stream, then they are suggested to upgrade to 4.0.4. If users are on 3.x, they are suggested to move to 3.21.4 or 3.22.1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23114
- https://github.com/apache/camel/pull/12759
- https://github.com/apache/camel/pull/12760
- https://github.com/apache/camel/pull/12761
- https://github.com/apache/camel/pull/12762
- https://github.com/apache/camel/pull/12790
- https://camel.apache.org/security/CVE-2024-23114.html
- https://github.com/Croway/potential-cassandra
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-20306
