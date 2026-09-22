# [H] Privilege escalation vulnerability in Apache Hadoop

## Summary
Severity: High
Advisory: GHSA-37pw-qw47-4jxm
CVE: CVE-2018-8029
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-05-31
Source: https://github.com/advisories/GHSA-37pw-qw47-4jxm
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-main` — affected >=2.2.0 <2.8.4
- Maven: `org.apache.hadoop:hadoop-main` — affected >=2.9.0 <2.9.2
- Maven: `org.apache.hadoop:hadoop-main` — affected >=3.0.0 <3.1.1

## Details
In Apache Hadoop versions 3.0.0-alpha1 to 3.1.0, 2.9.0 to 2.9.1, and 2.2.0 to 2.8.4, a user who can escalate to yarn user can possibly run arbitrary commands as root user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8029
- https://lists.apache.org/thread.html/0b8d58e02dbd0fb8bf7320c514fe58da1d6728bdc150f1ba04e0d9fc@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/17084c09e6dedf60efe08028b429c92ffd28aacc28454e4fa924578a@%3Cgeneral.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/a0164b87660223a2d491f83c88f905fe1a9fa8dc795148d9b0d968c8@%3Cdev.hbase.apache.org%3E
- https://lists.apache.org/thread.html/a97c53a81e639ca2fc7b8f61a4fcd1842c2a78544041244a7c624727@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r4dddf1705dbedfa94392913b2dad1cd2d1d89040facd389eea0b3510@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rb21df54a4e39732ce653d2aa5672e36a792b59eb6717f2a06bb8d02a@%3Ccommits.druid.apache.org%3E
- https://security.netapp.com/advisory/ntap-20190617-0001
- http://www.securityfocus.com/bid/108518
