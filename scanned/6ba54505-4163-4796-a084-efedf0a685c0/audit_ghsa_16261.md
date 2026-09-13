# [M] Apache Commons Compress: OutOfMemoryError unpacking broken Pack200 file

## Summary
Severity: Medium
Advisory: GHSA-4265-ccf5-phj5
CVE: CVE-2024-26308
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-19
Source: https://github.com/advisories/GHSA-4265-ccf5-phj5
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-compress` — affected >=1.21 <1.26.0

## Details
Allocation of Resources Without Limits or Throttling vulnerability in Apache Commons Compress. This issue affects Apache Commons Compress: from 1.21 before 1.26.

Users are recommended to upgrade to version 1.26, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-26308
- https://github.com/apache/commons-compress
- https://lists.apache.org/thread/ch5yo2d21p7vlqrhll9b17otbyq4npfg
- https://security.netapp.com/advisory/ntap-20240307-0009
- http://www.openwall.com/lists/oss-security/2024/02/19/2
