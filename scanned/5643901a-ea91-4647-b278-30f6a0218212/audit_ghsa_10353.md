# [H] Apache Thrift Node.js bindings vulnerable to Uncontrolled Recursion

## Summary
Severity: High
Advisory: GHSA-r67j-r569-jrwp
CVE: CVE-2026-41636
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-r67j-r569-jrwp
Type: github-advisory

## Affected
- npm: `thrift` — affected >=0 <0.23.0

## Details
Uncontrolled Recursion vulnerability in Apache Thrift Node.js bindings

This issue affects Apache Thrift: before 0.23.0.

Users are recommended to upgrade to version 0.23.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41636
- https://github.com/apache/thrift
- https://lists.apache.org/thread/lb4j0zyd5f3g36cos0wql925przpnwql
- http://www.openwall.com/lists/oss-security/2026/04/28/1
