# [C] Missing Authentication for Critical Function in Apache Cassandra

## Summary
Severity: Critical
Advisory: GHSA-52gq-7j6c-xw6x
CVE: CVE-2018-8016
CWE: CWE-306
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-52gq-7j6c-xw6x
Type: github-advisory

## Affected
- Maven: `org.apache.cassandra:cassandra-all` — affected >=3.8 <3.11.2

## Details
The default configuration in Apache Cassandra 3.8 through 3.11.1 binds an unauthenticated JMX/RMI interface to all network interfaces, which allows remote attackers to execute arbitrary Java code via an RMI request. This issue is a regression of CVE-2015-0225. The regression was introduced in https://issues.apache.org/jira/browse/CASSANDRA-12109. The fix for the regression is implemented in https://issues.apache.org/jira/browse/CASSANDRA-14173. This fix is contained in the 3.11.2 release of Apache Cassandra.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8016
- https://github.com/beobal/cassandra/commit/28ee665b3c0c9238b61a871064f024d54cddcc79
- https://issues.apache.org/jira/browse/CASSANDRA-14173
- https://lists.apache.org/thread.html/bafb9060bbdf958a1c15ba66c68531116fba4a83858a2796254da066@%3Cuser.cassandra.apache.org%3E
