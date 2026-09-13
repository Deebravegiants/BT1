# [H] Authentication bypass in Apache Hadoop

## Summary
Severity: High
Advisory: GHSA-4fh8-pm7g-pmxq
CVE: CVE-2018-11764
CWE: CWE-306
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-4fh8-pm7g-pmxq
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-main` — affected >=3.0.0-alpha4 <3.0.1
- Maven: `org.apache.hadoop:hadoop-main` — affected >=3.0.0-beta1 <3.0.1
- Maven: `org.apache.hadoop:hadoop-main` — affected >=3.0.0 <3.0.1

## Details
Web endpoint authentication check is broken in Apache Hadoop 3.0.0-alpha4, 3.0.0-beta1, and 3.0.0. Authenticated users may impersonate any user even if no proxy user is configured.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11764
- https://lists.apache.org/thread.html/r790ad0a049cde713b93589ecfd4dd2766fda0fc6807eedb6cf69f5c1%40%3Cgeneral.hadoop.apache.org%3E
- https://security.netapp.com/advisory/ntap-20201103-0003
