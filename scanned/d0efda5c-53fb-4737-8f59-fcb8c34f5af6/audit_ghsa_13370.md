# [H] Apache Cassandra: Privilege escalation when enabling FQL/Audit logs

## Summary
Severity: High
Advisory: GHSA-m9p2-j4hg-g373
CVE: CVE-2023-30601
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-m9p2-j4hg-g373
Type: github-advisory

## Affected
- Maven: `org.apache.cassandra:cassandra-all` — affected >=4.1.0 <4.1.2
- Maven: `org.apache.cassandra:cassandra-all` — affected >=4.0.0 <4.0.10

## Details
Privilege escalation when enabling FQL/Audit logs allows user with JMX access to run arbitrary commands as the user running Apache Cassandra
This issue affects Apache Cassandra: from 4.0.0 through 4.0.9, from 4.1.0 through 4.1.1.

WORKAROUND
The vulnerability requires nodetool/JMX access to be exploitable, disable access for any non-trusted users.

MITIGATION
Upgrade to 4.0.10 or 4.1.2 and leave the new FQL/Auditlog configuration property allow_nodetool_archive_command as false.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30601
- https://github.com/apache/cassandra/commit/22d74c711658507addfd67e2c78b04a9b88413b2
- https://github.com/apache/cassandra/commit/aafb4d19448f12ce600dc4e84a5b181308825b32
- https://github.com/apache/cassandra
- https://issues.apache.org/jira/browse/CASSANDRA-18550
- https://lists.apache.org/thread/f74p9jdhmmp7vtrqd8lgm8bq3dhxl8vn
