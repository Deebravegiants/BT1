# [H] Apache Thrift: Unbounded Read Leading to Denial of Service

## Summary
Severity: High
Advisory: BIT-thrift-2026-45112
Aliases: CVE-2026-45112
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-thrift-2026-45112
Type: osv

## Affected
- Bitnami: `thrift` — affected >=0.19.0 <0.24.0

## Details
Allocation of Resources Without Limits or Throttling vulnerability in Apache Thrift Java bindings.

This issue affects Apache Thrift: from 0.19.0 before 0.24.0.

Users are recommended to upgrade to version 0.24.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/34
- https://lists.apache.org/thread/7v3jhgwfbmhx42424phydlnzb109g8b9
- https://lists.apache.org/thread/hl9kmf1z2o3lxvspoj3g9ykl8lj9mdxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-45112
