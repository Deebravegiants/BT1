# [M] Apache Zeppelin Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g64r-xf39-q4p5
CVE: CVE-2024-31860
CWE: CWE-20, CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-g64r-xf39-q4p5
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin-server` — affected >=0.9.0 <0.11.0

## Details
Improper Input Validation vulnerability in Apache Zeppelin.

By adding relative path indicators (e.g `..`), attackers can see the contents for any files in the filesystem that the server account can access. 
This issue affects Apache Zeppelin from 0.9.0 before 0.11.0.

Users are recommended to upgrade to version 0.11.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31860
- https://github.com/apache/zeppelin/pull/4632
- https://github.com/apache/zeppelin/commit/f025a697c1d1d0264064d5adf6cb0b20d85041b6
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread/c0zfjnow3oc3dzc8w5rbkzj8lqj5jm5x
- http://www.openwall.com/lists/oss-security/2024/04/09/2
