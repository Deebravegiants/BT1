# [H] Apache Thrift: Node.js quadratic-time DoS in server receive transports

## Summary
Severity: High
Advisory: BIT-thrift-2026-55968
Aliases: CVE-2026-55968
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-thrift-2026-55968
Type: osv

## Affected
- Bitnami: `thrift` — affected >=0 <0.24.0

## Details
Inefficient Algorithmic Complexity, Allocation of Resources Without Limits or Throttling vulnerability in Apache Thrift Node.js bindings.

This issue affects Apache Thrift: before 0.24.0.

Users are recommended to upgrade to version 0.24.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/39
- https://lists.apache.org/thread/7v3jhgwfbmhx42424phydlnzb109g8b9
- https://lists.apache.org/thread/gxhhfyr6flr5vzr4qnxm13p6fc41qstp
- https://nvd.nist.gov/vuln/detail/CVE-2026-55968
