# [H] Apache Hadoop's LinuxContainerExecutor runs docker commands as root with insufficient input validation

## Summary
Severity: High
Advisory: GHSA-h24p-qwf4-84q8
CVE: CVE-2017-7669
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-h24p-qwf4-84q8
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-common` — affected >=0 <2.8.1
- Maven: `org.apache.hadoop:hadoop-common` — affected >=3.0.0-alpha1 <3.0.0-alpha3

## Details
In Apache Hadoop 2.8.0, 3.0.0-alpha1, and 3.0.0-alpha2, the LinuxContainerExecutor runs docker commands as root with insufficient input validation. When the docker feature is enabled, authenticated users can run commands as root. This issue is fixed in versions 2.8.1 and 3.0.0-alpha3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7669
- https://mail-archives.apache.org/mod_mbox/hadoop-user/201706.mbox/%3C4A2FDA56-491B-4C2A-915F-C9D4A4BDB92A%40apache.org%3E
- http://www.securityfocus.com/bid/98795
