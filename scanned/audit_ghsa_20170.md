# [H] User account escalation in Apache Hadoop

## Summary
Severity: High
Advisory: GHSA-58jx-f5rf-qgqf
CVE: CVE-2021-33036
CWE: CWE-22, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-58jx-f5rf-qgqf
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-yarn-server-common` — affected >=2.2.0 <2.10.2
- Maven: `org.apache.hadoop:hadoop-yarn-server-common` — affected >=3.0.0 <3.2.3
- Maven: `org.apache.hadoop:hadoop-yarn-server-common` — affected >=3.3.0 <3.3.2

## Details
In Apache Hadoop 2.2.0 to 2.10.1, 3.0.0-alpha1 to 3.1.4, 3.2.0 to 3.2.2, and 3.3.0 to 3.3.1, a user who can escalate to yarn user can possibly run arbitrary commands as root user. Users should upgrade to Apache Hadoop 2.10.2, 3.2.3, 3.3.2 or higher.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33036
- https://github.com/apache/hadoop/commit/227d64ab59e8aa6477769b2542ad0cd7a6d855cb
- https://github.com/apache/hadoop/commit/45801fba8b00257ab32c02a7d1a05948ba687a49
- https://github.com/apache/hadoop/commit/ba041fe6d34215f075e0a7b2078d7273147e14b7
- https://github.com/apache/hadoop
- https://lists.apache.org/thread/ctr84rmo3xd2tzqcx2b277c8z692vhl5
- https://security.netapp.com/advisory/ntap-20220722-0003
- http://www.openwall.com/lists/oss-security/2022/06/15/2
