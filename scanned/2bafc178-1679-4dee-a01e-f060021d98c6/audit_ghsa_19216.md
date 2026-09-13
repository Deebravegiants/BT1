# [M] Apache Cassandra: unrestricted deserialization of JMX authentication credentials

## Summary
Severity: Medium
Advisory: GHSA-rgfx-7p65-3ff4
CVE: CVE-2024-27137
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-02-04
Source: https://github.com/advisories/GHSA-rgfx-7p65-3ff4
Type: github-advisory

## Affected
- Maven: `org.apache.cassandra:cassandra-all` — affected >=5.0-beta1 <5.0.3
- Maven: `org.apache.cassandra:cassandra-all` — affected >=4.1.0 <4.1.8
- Maven: `org.apache.cassandra:cassandra-all` — affected >=4.0.2 <4.0.15

## Details
In Apache Cassandra it is possible for a local attacker without access to the Apache Cassandra process or configuration files to manipulate the RMI registry to perform a man-in-the-middle attack and capture user names and passwords used to access the JMX interface. The attacker can then use these credentials to access the JMX interface and perform unauthorized operations.

This is same vulnerability that CVE-2020-13946 was issued for, but the Java option was changed in JDK10.

This issue affects Apache Cassandra from 4.0.2 through 5.0.2 running Java 11.

Operators are recommended to upgrade to a release equal to or later than 4.0.15, 4.1.8, or 5.0.3 which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27137
- https://github.com/apache/cassandra
- https://lists.apache.org/thread/jsk87d9yv8r204mgqpz1qxtp5wcrpysm
- https://security.netapp.com/advisory/ntap-20250214-0004
