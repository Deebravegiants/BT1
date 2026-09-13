# [H] Apache Portable Runtime Utility: Heap buffer overflow in APR redis client

## Summary
Severity: High
Advisory: BIT-apr-util-2026-34501
Aliases: CVE-2026-34501
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-apr-util-2026-34501
Type: osv

## Affected
- Bitnami: `apr-util` — affected >=1.6.0 <1.6.4

## Details
Heap-based Buffer Overflow vulnerability in Apache Portable Runtime Utility redis client.

This issue affects Apache Portable Runtime Utility: from 1.6.0 through 1.6.3.

Users are recommended to upgrade to version 1.6.4, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/11
- https://lists.apache.org/thread/o8h6c7cq86fplxlnry6c3rn9x0ovq8mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34501
