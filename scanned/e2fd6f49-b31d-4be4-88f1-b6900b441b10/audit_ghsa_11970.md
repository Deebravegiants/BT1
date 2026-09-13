# [H] Apache ZooKeeper has improper handling of configuration values

## Summary
Severity: High
Advisory: GHSA-crhr-qqj8-rpxc
CVE: CVE-2026-24308
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-crhr-qqj8-rpxc
Type: github-advisory

## Affected
- Maven: `org.apache.zookeeper:zookeeper` — affected >=3.9.0 <3.9.5
- Maven: `org.apache.zookeeper:zookeeper` — affected >=3.8.0 <3.8.6

## Details
Improper handling of configuration values in ZKConfig in Apache ZooKeeper 3.8.5 and 3.9.4 on all platforms allows an attacker to expose sensitive information stored in client configuration in the client's logfile. Configuration values are exposed at INFO level logging rendering potential production systems affected by the issue. Users are recommended to upgrade to version 3.8.6 or 3.9.5 which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24308
- https://github.com/apache/zookeeper
- https://github.com/apache/zookeeper/releases/tag/release-3.8.6
- https://github.com/apache/zookeeper/releases/tag/release-3.9.5
- https://lists.apache.org/thread/qng3rtzv2pqkmko4rhv85jfplkyrgqdr
- http://www.openwall.com/lists/oss-security/2026/03/07/5
