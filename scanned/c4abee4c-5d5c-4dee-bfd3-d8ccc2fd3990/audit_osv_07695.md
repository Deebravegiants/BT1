# [H] Apache Thrift: C++ TSSLSocket matchName() RFC 6125 Wildcard Bypass

## Summary
Severity: High
Advisory: BIT-thrift-2026-48145
Aliases: CVE-2026-48145
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-thrift-2026-48145
Type: osv

## Affected
- Bitnami: `thrift` — affected >=0 <0.24.0

## Details
Improper Validation of Certificate with Host Mismatch vulnerability in Apache Thrift C++ bindings.

This issue affects Apache Thrift: before 0.24.0.

Users are recommended to upgrade to version 0.24.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/36
- https://lists.apache.org/thread/2popgc4ks1l87jjho1w5fpk5k4x06b7h
- https://lists.apache.org/thread/7v3jhgwfbmhx42424phydlnzb109g8b9
- https://nvd.nist.gov/vuln/detail/CVE-2026-48145
