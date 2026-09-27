# [C] Apache Hadoop heap overflow before v2.10.2, v3.2.3, v3.3.2

## Summary
Severity: Critical
Advisory: GHSA-rmpj-7c96-mrg8
CVE: CVE-2021-37404
CWE: CWE-120, CWE-131, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-14
Source: https://github.com/advisories/GHSA-rmpj-7c96-mrg8
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-common` — affected >=3.3.0 <3.3.2
- Maven: `org.apache.hadoop:hadoop-common` — affected >=3.0.0 <3.2.3
- Maven: `org.apache.hadoop:hadoop-common` — affected >=0 <2.10.2

## Details
There is a potential heap buffer overflow in Apache Hadoop libhdfs native code. Opening a file path provided by user without validation may result in a denial of service or arbitrary code execution. Users should upgrade to Apache Hadoop 2.10.2, 3.2.3, 3.3.2 or higher.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37404
- https://github.com/apache/hadoop
- https://lists.apache.org/thread/2h56ztcj3ojc66qzf1nno88vjw9vd4wo
- https://security.netapp.com/advisory/ntap-20220715-0007
