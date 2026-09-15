# [H] Apache ZooKeeper: Reverse-DNS fallback enables hostname verification bypass in ZooKeeper ZKTrustManager

## Summary
Severity: High
Advisory: GHSA-7xrh-hqfc-g7qr
CVE: CVE-2026-24281
CWE: CWE-295, CWE-297
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-7xrh-hqfc-g7qr
Type: github-advisory

## Affected
- Maven: `org.apache.zookeeper:zookeeper` — affected >=3.8.0 <3.8.6
- Maven: `org.apache.zookeeper:zookeeper` — affected >=3.9.0 <3.9.5

## Details
Hostname verification in Apache ZooKeeper ZKTrustManager falls back to reverse DNS (PTR) when IP SAN validation fails, allowing attackers who control or spoof PTR records to impersonate ZooKeeper servers or clients with a valid certificate for the PTR name. It's important to note that attacker must present a certificate which is trusted by ZKTrustManager which makes the attack vector harder to exploit. Users are recommended to upgrade to version 3.8.6 or 3.9.5, which fixes this issue by introducing a new configuration option to disable reverse DNS lookup in client and quorum protocols.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24281
- https://github.com/apache/zookeeper/commit/66c4efecdda1302d9cfb3af9eedb122b74452bf3
- https://github.com/apache/zookeeper
- https://issues.apache.org/jira/browse/ZOOKEEPER-4986
- https://lists.apache.org/thread/088ddsbrzhd5lxzbqf5n24yg0mwh9jt2
- http://www.openwall.com/lists/oss-security/2026/03/07/4
