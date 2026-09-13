# [H] Apache Thrift: Rust binary protocol non-strict path missing string size limit

## Summary
Severity: High
Advisory: BIT-thrift-2026-58389
Aliases: CVE-2026-58389
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-thrift-2026-58389
Type: osv

## Affected
- Bitnami: `thrift` — affected >=0 <0.24.0

## Details
Allocation of Resources Without Limits or Throttling vulnerability in Apache Thrift Rust bindings.

This issue affects Apache Thrift: before 0.24.0.

Users are recommended to upgrade to version 0.24.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/44
- https://lists.apache.org/thread/7v3jhgwfbmhx42424phydlnzb109g8b9
- https://lists.apache.org/thread/ht2mjt8m3vz9v0h5pqzvc4r4nzfxwtrw
- https://nvd.nist.gov/vuln/detail/CVE-2026-58389
