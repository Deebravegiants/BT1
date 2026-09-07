# [M] Apache Cassandra: CassandraNetworkAuthorizer and CassandraCIDRAuthorizer can be bypassed allowing access to different network regions

## Summary
Severity: Medium
Advisory: GHSA-3cjf-fwcq-xh22
CVE: CVE-2025-24860
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-02-04
Source: https://github.com/advisories/GHSA-3cjf-fwcq-xh22
Type: github-advisory

## Affected
- Maven: `org.apache.cassandra:cassandra-all` — affected >=4.0-alpha1 <4.0.16
- Maven: `org.apache.cassandra:cassandra-all` — affected >=4.1-alpha1 <4.1.8
- Maven: `org.apache.cassandra:cassandra-all` — affected >=5.0-alpha1 <5.0.3

## Details
Incorrect Authorization vulnerability in Apache Cassandra allowing users to access a datacenter or IP/CIDR groups they should not be able to when using CassandraNetworkAuthorizer or CassandraCIDRAuthorizer. 

Users with restricted data center access can update their own permissions via data control language (DCL) statements on affected versions.

This issue affects Apache Cassandra: from 4.0.0 through 4.0.15 and from 4.1.0 through 4.1.7 for CassandraNetworkAuthorizer, and from 5.0.0 through 5.0.2 for both CassandraNetworkAuthorizer and CassandraCIDRAuthorizer.

Operators using CassandraNetworkAuthorizer or CassandraCIDRAuthorizer on affected versions should review data access rules for potential breaches. Users are recommended to upgrade to versions 4.0.16, 4.1.8, 5.0.3, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24860
- https://github.com/apache/cassandra
- https://lists.apache.org/thread/yjo5on4tf7s1r9qklc4byrz30b8vkm2d
- https://security.netapp.com/advisory/ntap-20250214-0005
- http://www.openwall.com/lists/oss-security/2025/02/03/3
