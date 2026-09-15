# [H] Missing Authorization in Apache ZooKeeper

## Summary
Severity: High
Advisory: GHSA-ccqf-c5hq-77mp
CVE: CVE-2018-8012
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-ccqf-c5hq-77mp
Type: github-advisory

## Affected
- Maven: `org.apache.zookeeper:zookeeper` — affected >=0 <3.4.10
- Maven: `org.apache.zookeeper:zookeeper` — affected >=3.5.0-alpha <3.5.4-beta

## Details
No authentication/authorization is enforced when a server attempts to join a quorum in Apache ZooKeeper before 3.4.10, and 3.5.0-alpha through 3.5.3-beta. As a result an arbitrary end point could join the cluster and begin propagating counterfeit changes to the leader.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8012
- https://lists.apache.org/thread.html/053d9ce4d579b02203db18545fee5e33f35f2932885459b74d1e4272@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/bcce5a9c532b386c68dab2f6b3ce8b0cc9b950ec551766e76391caa3@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/c75147028c1c79bdebd4f8fa5db2b77da85de2b05ecc0d54d708b393@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r73daf1fc5d85677d9a854707e1908d14e174b7bbb0c603709c0ab33f@%3Coak-commits.jackrabbit.apache.org%3E
- https://lists.apache.org/thread.html/r8f0d920805af93033c488af89104e2d682662bacfb8406db865d5e14@%3Cdev.jackrabbit.apache.org%3E
- https://lists.apache.org/thread.html/rc5bc4ddb0deabf8cfb69378cecee56fcdc76929bea9e6373cb863870@%3Cdev.jackrabbit.apache.org%3E
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/re3a4048e9515d4afea416df907a612ed384a16c57cf99e97ee4a12f2@%3Cdev.jackrabbit.apache.org%3E
- https://www.debian.org/security/2018/dsa-4214
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://www.securityfocus.com/bid/104253
- http://www.securitytracker.com/id/1040948
