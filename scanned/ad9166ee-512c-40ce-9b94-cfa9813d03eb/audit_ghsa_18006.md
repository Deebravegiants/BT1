# [M] Apache Zeppelin: XSS in the Helium module

## Summary
Severity: Medium
Advisory: GHSA-p288-459w-jxj6
CVE: CVE-2024-41177
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-08-03
Source: https://github.com/advisories/GHSA-p288-459w-jxj6
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin-web` — affected >=0 <0.12.0

## Details
Incomplete Blacklist to Cross-Site Scripting vulnerability in Apache Zeppelin.

This issue affects Apache Zeppelin: before 0.12.0.

Users are recommended to upgrade to version 0.12.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41177
- https://github.com/apache/zeppelin/pull/4755
- https://github.com/apache/zeppelin/pull/4795
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread/nwh8vh9f3pnvt04n8z4g2kbddh62blr6
- http://www.openwall.com/lists/oss-security/2025/08/03/4
