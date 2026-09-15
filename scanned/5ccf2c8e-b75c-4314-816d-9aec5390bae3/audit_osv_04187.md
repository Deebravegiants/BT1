# [C] Apache Portable Runtime Utility: apr-util XML stack recursion crash

## Summary
Severity: Critical
Advisory: BIT-apr-util-2026-32327
Aliases: CVE-2026-32327
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-apr-util-2026-32327
Type: osv

## Affected
- Bitnami: `apr-util` — affected >=0 <1.6.4

## Details
A bug in APR-util version 1.6.3 (and earlier) allows a stack recursion attack against any library consumer which parses XML from untrusted sources and uses the apr_xml_quote_elem() function.

Users are recommended to upgrade to version 1.6.4, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/9
- https://lists.apache.org/thread/hq27vj8yfno9tkwv0fpj6jksfzgxvth1
- https://nvd.nist.gov/vuln/detail/CVE-2026-32327
