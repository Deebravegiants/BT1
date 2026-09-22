# [H] Apache Thrift, Apache Thrift, Apache Thrift, Apache Thrift, Apache Thrift, Apache Thrift: integer overflow in TProtocol::checkReadBytesAvailable()

## Summary
Severity: High
Advisory: BIT-thrift-2026-55969
Aliases: CVE-2026-55969
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-thrift-2026-55969
Type: osv

## Affected
- Bitnami: `thrift` — affected >=0 <0.24.0

## Details
Integer Overflow or Wraparound vulnerability in Apache Thrift C++, c_glib, Go, netstd, Delphi and Haxe bindings.

This issue affects Apache Thrift: before 0.24.0.

Users are recommended to upgrade to version 0.24.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/40
- https://lists.apache.org/thread/7v3jhgwfbmhx42424phydlnzb109g8b9
- https://lists.apache.org/thread/xmkgd107k795hyrg5kf97mny30sgl5bo
- https://nvd.nist.gov/vuln/detail/CVE-2026-55969
