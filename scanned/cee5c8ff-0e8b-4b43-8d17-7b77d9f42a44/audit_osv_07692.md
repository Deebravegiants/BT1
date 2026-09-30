# [H] Apache Thrift: Node.js web_server.js multi-vulnerability

## Summary
Severity: High
Advisory: BIT-thrift-2026-43870
Aliases: CVE-2026-43870, GHSA-526f-jxpj-jmg2
Ecosystem: Bitnami
Published: 2026-05-07
Source: https://osv.dev/vulnerability/BIT-thrift-2026-43870
Type: osv

## Affected
- Bitnami: `thrift` — affected >=0 <0.23.0

## Details
Origin Validation Error, Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'), Improper Neutralization of CRLF Sequences in HTTP Headers ('HTTP Request/Response Splitting'), Uncontrolled Resource Consumption vulnerability in Apache Thrift.

This issue affects Apache Thrift: before 0.23.0.

Users are recommended to upgrade to version 0.23.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/05/4
- https://lists.apache.org/thread/pgtfq44ltc9t63kxcbqmwqzt45pnhqdy
- https://nvd.nist.gov/vuln/detail/CVE-2026-43870
