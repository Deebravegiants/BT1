# [C] Apache Thrift: c_glib TLS Client Missing Hostname Verification

## Summary
Severity: Critical
Advisory: BIT-thrift-2026-48144
Aliases: CVE-2026-48144
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-thrift-2026-48144
Type: osv

## Affected
- Bitnami: `thrift` — affected >=0 <0.24.0

## Details
Improper Validation of Certificate with Host Mismatch vulnerability in Apache Thrift c_glib bindings.

This issue affects Apache Thrift: before 0.24.0.

Users are recommended to upgrade to version 0.24.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/35
- https://lists.apache.org/thread/2xoltfxgzf5jyhcwq6y07spts5cn6ppj
- https://lists.apache.org/thread/7v3jhgwfbmhx42424phydlnzb109g8b9
- https://nvd.nist.gov/vuln/detail/CVE-2026-48144
