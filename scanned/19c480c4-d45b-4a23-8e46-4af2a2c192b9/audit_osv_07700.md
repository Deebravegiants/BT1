# [C] Apache Thrift: C++ ZLIB heap buffer overflow (write) in THeaderTransport::untransform()

## Summary
Severity: Critical
Advisory: BIT-thrift-2026-55971
Aliases: CVE-2026-55971
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-thrift-2026-55971
Type: osv

## Affected
- Bitnami: `thrift` — affected >=0 <0.24.0

## Details
Heap-based Buffer Overflow vulnerability in Apache Thrift C++ bindings.

This issue affects Apache Thrift: before 0.24.0.

Users are recommended to upgrade to version 0.24.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/42
- https://lists.apache.org/thread/7v3jhgwfbmhx42424phydlnzb109g8b9
- https://lists.apache.org/thread/xjs36m6kjxpmrmzwck636msg3nvoqnmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-55971
