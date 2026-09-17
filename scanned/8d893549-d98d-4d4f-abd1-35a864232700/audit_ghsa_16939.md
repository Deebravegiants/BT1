# [M] Apache Zeppelin: Replacing other users notebook, bypassing any permissions

## Summary
Severity: Medium
Advisory: GHSA-m65c-wmw9-vmpp
CVE: CVE-2024-31863
CWE: CWE-290
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-m65c-wmw9-vmpp
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin-server` — affected >=0.10.1 <0.11.0

## Details
Authentication Bypass by Spoofing vulnerability by replacing to exsiting notes in Apache Zeppelin. This issue affects Apache Zeppelin: from 0.10.1 before 0.11.0.

Users are recommended to upgrade to version 0.11.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31863
- https://github.com/apache/zeppelin/commit/f025a697c1d1d0264064d5adf6cb0b20d85041b6
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread/3od2gfpwllmtc9c5ggw04ohn8s7w3ct9
- http://www.openwall.com/lists/oss-security/2024/04/09/6
