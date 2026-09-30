# [H] Apache Thrift Python, Go, PHP and Java bindings have an Infinite Loop

## Summary
Severity: High
Advisory: GHSA-8wv5-x4w7-5gww
CVE: CVE-2026-43871
CWE: CWE-835
Ecosystem: Go, Maven, Packagist, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-27
Source: https://github.com/advisories/GHSA-8wv5-x4w7-5gww
Type: github-advisory

## Affected
- PyPI: `thrift` — affected >=0 <0.24.0
- Go: `github.com/apache/thrift` — affected >=0 <0.24.0
- Packagist: `apache/thrift` — affected >=0 <0.24.0
- Maven: `org.apache.thrift:libthrift` — affected >=0 <0.24.0

## Details
Loop with Unreachable Exit Condition ('Infinite Loop') vulnerability in Apache Thrift Python, Go, PHP and Java bindings.This issue affects Apache Thrift: before 0.24.0.

Users are recommended to upgrade to version 0.24.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43871
- https://github.com/apache/thrift
- https://lists.apache.org/thread/7v3jhgwfbmhx42424phydlnzb109g8b9
- https://lists.apache.org/thread/l4dwf14zbyqsmkc28c99ojj3t3gg9qby
- http://www.openwall.com/lists/oss-security/2026/07/24/33
