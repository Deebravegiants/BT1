# [M] Apache Cassandra has sensitive Information Leak in cqlsh

## Summary
Severity: Medium
Advisory: GHSA-fh34-c629-p8xj
CVE: CVE-2026-27315
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-fh34-c629-p8xj
Type: github-advisory

## Affected
- Maven: `org.apache.cassandra:cassandra-all` — affected >=4.0 <4.0.20

## Details
Sensitive Information Leak in cqlsh in Apache Cassandra 4.0 allows access to sensitive information, like passwords, from previously executed cqlsh command via  ~/.cassandra/cqlsh_history local file access.

Users are recommended to upgrade to version 4.0.20, which fixes this issue.

--
Description: Cassandra's command-line tool, cqlsh, provides a command history feature that allows users to recall previously executed commands using the up/down arrow keys. These history records are saved in the ~/.cassandra/cqlsh_history file in the user's home directory.

However, cqlsh does not redact sensitive information when saving command history. This means that if a user executes operations involving passwords (such as logging in or creating users) within cqlsh, these passwords are permanently stored in cleartext in the history file on the disk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27315
- https://github.com/apache/cassandra
- https://issues.apache.org/jira/browse/CASSANDRA-21180
- https://lists.apache.org/thread/ft77zrk2mzt8qsch4g6jqjj4901d22k3
- http://www.openwall.com/lists/oss-security/2026/04/07/8
