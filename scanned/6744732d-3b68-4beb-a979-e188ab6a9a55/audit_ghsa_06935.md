# [H] Apache Thrift Python bindings have an Improper Handling of Highly Compressed Data (Data Amplification) vulnerability

## Summary
Severity: High
Advisory: GHSA-6pjx-3pjc-mrj8
CVE: CVE-2026-41608
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-27
Source: https://github.com/advisories/GHSA-6pjx-3pjc-mrj8
Type: github-advisory

## Affected
- PyPI: `thrift` — affected >=0 <0.24.0

## Details
Improper Handling of Highly Compressed Data (Data Amplification) vulnerability in Apache Thrift Python bindings.

This issue affects Apache Thrift: before 0.24.0.

Users are recommended to upgrade to version 0.24.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41608
- https://github.com/apache/thrift
- https://lists.apache.org/thread/7v3jhgwfbmhx42424phydlnzb109g8b9
- https://lists.apache.org/thread/vwsbcwqdpwdtp8qkjo11ol6rodbfm21f
- http://www.openwall.com/lists/oss-security/2026/07/24/32
