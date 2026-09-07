# [H] Deserialization of Untrusted Data in Apache Hadoop YARN

## Summary
Severity: High
Advisory: GHSA-rr2m-gffv-mgrj
CVE: CVE-2021-25642
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-26
Source: https://github.com/advisories/GHSA-rr2m-gffv-mgrj
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-yarn-server` — affected >=0 <2.10.2
- Maven: `org.apache.hadoop:hadoop-yarn-server` — affected >=3.0.0 <3.2.4
- Maven: `org.apache.hadoop:hadoop-yarn-server` — affected >=3.3.0 <3.3.4

## Details
ZKConfigurationStore which is optionally used by CapacityScheduler of Apache Hadoop YARN deserializes data obtained from ZooKeeper without validation. An attacker having access to ZooKeeper can run arbitrary commands as YARN user by exploiting this. Users should upgrade to Apache Hadoop 2.10.2, 3.2.4, 3.3.4 or later (containing YARN-11126) if ZKConfigurationStore is used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25642
- https://github.com/apache/hadoop/commit/5e2f4339fadc88f20543915fc9b0aaeaf4f9e7bf
- https://github.com/apache/hadoop
- https://lists.apache.org/thread/g6vf2h4wdgzzdgk91mqozhs58wotq150
- https://security.netapp.com/advisory/ntap-20221201-0003
