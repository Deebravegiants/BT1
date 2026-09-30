# [M] Access control bypass in Apache ZooKeeper

## Summary
Severity: Medium
Advisory: GHSA-2hw2-62cp-p9p7
CVE: CVE-2019-0201
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-05-29
Source: https://github.com/advisories/GHSA-2hw2-62cp-p9p7
Type: github-advisory

## Affected
- Maven: `org.apache.zookeeper:zookeeper` — affected >=1.0.0 <3.4.14
- Maven: `org.apache.zookeeper:zookeeper` — affected >=3.5.0 <3.5.5

## Details
An issue is present in Apache ZooKeeper 1.0.0 to 3.4.13 and 3.5.0-alpha to 3.5.4-beta. ZooKeeper?s getACL() command doesn?t check any permission when retrieves the ACLs of the requested node and returns all information contained in the ACL Id field as plaintext string. DigestAuthenticationProvider overloads the Id field with the hash value that is used for user authentication. As a consequence, if Digest Authentication is in use, the unsalted hash value will be disclosed by getACL() request for unauthenticated or unprivileged users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0201
- https://zookeeper.apache.org/security.html#CVE-2019-0201
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.debian.org/security/2019/dsa-4461
- https://security.netapp.com/advisory/ntap-20190619-0001
- https://seclists.org/bugtraq/2019/Jun/13
- https://lists.debian.org/debian-lts-announce/2019/05/msg00033.html
- https://lists.apache.org/thread.html/r40f32125c1d97ad82404cc918171d9e0fcf78e534256674e9da1eb4b@%3Ccommon-issues.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/f6112882e30a31992a79e0a8c31ac179e9d0de7c708de3a9258d4391@%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/5d9a1cf41a5880557bf680b7321b4ab9a4d206c601ffb15fef6f196a@%3Ccommits.accumulo.apache.org%3E
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/053d9ce4d579b02203db18545fee5e33f35f2932885459b74d1e4272@%3Cissues.activemq.apache.org%3E
- https://issues.apache.org/jira/browse/ZOOKEEPER-1392
- https://access.redhat.com/errata/RHSA-2019:4352
- https://access.redhat.com/errata/RHSA-2019:3892
- https://access.redhat.com/errata/RHSA-2019:3140
