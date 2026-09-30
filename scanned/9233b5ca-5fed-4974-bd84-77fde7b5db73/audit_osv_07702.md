# [C] Apache Thrift: C++ THeaderTransport::readString() info-header length bounds bypass

## Summary
Severity: Critical
Advisory: BIT-thrift-2026-58662
Aliases: CVE-2026-58662
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-thrift-2026-58662
Type: osv

## Affected
- Bitnami: `thrift` — affected >=0 <0.24.0

## Details
Improper Validation of Specified Quantity in Input, Out-of-bounds Read vulnerability in Apache Thrift C++ bindings.

This issue affects Apache Thrift: before 0.24.0.

Users are recommended to upgrade to version 0.24.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/45
- https://lists.apache.org/thread/13mzvylr3r3nktxrh5k1h30ng1t1sw1d
- https://lists.apache.org/thread/7v3jhgwfbmhx42424phydlnzb109g8b9
- https://nvd.nist.gov/vuln/detail/CVE-2026-58662
