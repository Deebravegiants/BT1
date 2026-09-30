# [H] Remote Code Execution in Apache Flume

## Summary
Severity: High
Advisory: GHSA-x5m7-rwfx-w7qm
CVE: CVE-2022-25167
Ecosystem: Maven
Published: 2022-06-15
Source: https://github.com/advisories/GHSA-x5m7-rwfx-w7qm
Type: github-advisory

## Affected
- Maven: `org.apache.flume.flume-ng-sources:flume-jms-source` — affected >=1.4.0 <1.10.0

## Details
Apache Flume versions 1.4.0 through 1.9.0 are vulnerable to a remote code execution (RCE) attack when a configuration uses a JMS Source with a JNDI LDAP data source URI when an attacker has control of the target LDAP server. This issue is fixed by limiting JNDI to allow only the use of the java protocol or no protocol.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25167
- https://github.com/apache/flume/commit/dafb26ccb172141c6e14e95447e1b6ae38e9a7d0
- https://github.com/apache/flume
- https://issues.apache.org/jira/browse/FLUME-3416
- https://lists.apache.org/thread/16nf6b81zjpdc4y93ho99oxo83ddbsvg
- http://www.openwall.com/lists/oss-security/2022/06/14/1
