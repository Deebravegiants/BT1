# [M] Apache ZooKeeper vulnerable to information disclosure in persistent watchers handling

## Summary
Severity: Medium
Advisory: GHSA-r978-9m6m-6gm6
CVE: CVE-2024-23944
CWE: CWE-200, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-15
Source: https://github.com/advisories/GHSA-r978-9m6m-6gm6
Type: github-advisory

## Affected
- Maven: `org.apache.zookeeper:zookeeper` — affected >=3.8.0 <3.8.4
- Maven: `org.apache.zookeeper:zookeeper` — affected >=3.9.0 <3.9.2
- Maven: `org.apache.zookeeper:zookeeper` — affected >=3.6.0

## Details
Information disclosure in persistent watchers handling in Apache ZooKeeper due to missing ACL check. It allows an attacker to monitor child znodes by attaching a persistent watcher (addWatch command) to a parent which the attacker has already access to. ZooKeeper server doesn't do ACL check when the persistent watcher is triggered and as a consequence, the full path of znodes that a watch event gets triggered upon is exposed to the owner of the watcher. It's important to note that only the path is exposed by this vulnerability, not the data of znode, but since znode path can contain sensitive information like user name or login ID, this issue is potentially critical.

Users are recommended to upgrade to version 3.9.2, 3.8.4 which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23944
- https://github.com/apache/zookeeper/commit/29c7b9462681f47c2ac12e609341cf9f52abac5c
- https://github.com/apache/zookeeper/commit/65b91d2d9a56157285c2a86b106e67c26520b01d
- https://github.com/apache/zookeeper/commit/daf7cfd04005cff1a4f7cab5ab13d41db88d0cd8
- https://github.com/apache/zookeeper
- https://lists.apache.org/thread/96s5nqssj03rznz9hv58txdb2k1lr79k
- http://www.openwall.com/lists/oss-security/2024/03/14/2
