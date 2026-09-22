# [M] Apache Linkis DataSource: DataSource module Oracle SQL Database Password Logged

## Summary
Severity: Medium
Advisory: GHSA-m757-p8rv-4q93
CVE: CVE-2023-50740
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-m757-p8rv-4q93
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis` — affected >=0 <1.5.0

## Details
In Apache Linkis <=1.4.0, The password is printed to the log when using the Oracle data source of the Linkis data source module. 
We recommend users upgrade the version of Linkis to version 1.5.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50740
- https://github.com/apache/linkis/commit/08cbcfca140afebae10e1582ee87721578719ded
- https://github.com/apache/linkis
- https://lists.apache.org/thread/5o342chnpyd6rps68ygzfkzycxl998yo
- http://www.openwall.com/lists/oss-security/2024/03/06/2
