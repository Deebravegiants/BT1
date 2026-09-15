# [M] Apache Hive Information Exposure and Observable Timing Discrepancy

## Summary
Severity: Medium
Advisory: GHSA-54g4-5cf6-hjp3
CVE: CVE-2020-1926
CWE: CWE-200, CWE-203, CWE-208
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-54g4-5cf6-hjp3
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive` — affected >=0 <2.3.8

## Details
Apache Hive cookie signature verification used a non constant time comparison which is known to be vulnerable to timing attacks. This could allow recovery of another users cookie signature. The issue was addressed in Apache Hive 2.3.8

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1926
- https://issues.apache.org/jira/browse/HIVE-22708
- https://lists.apache.org/thread.html/rd186eedff68102ba1e68059a808101c5aa587e11542c7dcd26e7b9d7%40%3Cuser.hive.apache.org%3E
