# [M] Apache Zeppelin: Denial of service with invalid notebook name

## Summary
Severity: Medium
Advisory: GHSA-6623-c6mr-6737
CVE: CVE-2024-31862
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-6623-c6mr-6737
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin-server` — affected >=0.10.1 <0.11.0

## Details
Improper Input Validation vulnerability in Apache Zeppelin when creating a new note from Zeppelin's UI. This issue affects Apache Zeppelin from 0.10.1 before 0.11.0.

Users are recommended to upgrade to version 0.11.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31862
- https://github.com/apache/zeppelin/pull/4632
- https://github.com/apache/zeppelin/commit/f025a697c1d1d0264064d5adf6cb0b20d85041b6
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread/73xdjx43yg4yz8bd4p3o8vzyybkysmn0
- http://www.openwall.com/lists/oss-security/2024/04/09/5
