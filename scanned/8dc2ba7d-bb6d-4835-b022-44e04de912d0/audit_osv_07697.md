# [H] Apache Thrift: Ruby THeaderTransport ZLIB Decompression Bomb

## Summary
Severity: High
Advisory: BIT-thrift-2026-49158
Aliases: CVE-2026-49158
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-thrift-2026-49158
Type: osv

## Affected
- Bitnami: `thrift` — affected >=0 <0.24.0

## Details
Improper Handling of Highly Compressed Data (Data Amplification) vulnerability in Apache Thrift Ruby bindings.

This issue affects Apache Thrift: before 0.24.0.

Users are recommended to upgrade to version 0.24.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/38
- https://lists.apache.org/thread/7v3jhgwfbmhx42424phydlnzb109g8b9
- https://lists.apache.org/thread/fmjl8l415tj9zwlob8v2dr5hq1d0hts7
- https://nvd.nist.gov/vuln/detail/CVE-2026-49158
