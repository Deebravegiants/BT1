# [H] Apache Thrift TFramedTransport Go language implementation has an Integer Overflow or Wraparound vulnerability

## Summary
Severity: High
Advisory: GHSA-wf45-q9ch-q8gh
CVE: CVE-2026-41602
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-wf45-q9ch-q8gh
Type: github-advisory

## Affected
- Go: `github.com/apache/thrift` — affected >=0 <0.23.0

## Details
Integer Overflow or Wraparound vulnerability in Apache Thrift TFramedTransport Go language implementation

This issue affects Apache Thrift: before 0.23.0.

Users are recommended to upgrade to version 0.23.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41602
- https://github.com/apache/thrift
- https://lists.apache.org/thread/lb4j0zyd5f3g36cos0wql925przpnwql
- http://www.openwall.com/lists/oss-security/2026/04/28/6
