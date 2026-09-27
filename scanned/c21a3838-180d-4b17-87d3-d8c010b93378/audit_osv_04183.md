# [C] Apache Portable Runtime (APR): out-of-bound writes in the apr_encode family of functions

## Summary
Severity: Critical
Advisory: BIT-apr-2022-24963
Aliases: CVE-2022-24963
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apr-2022-24963
Type: osv

## Affected
- Bitnami: `apr` — affected >=1.7.0 <1.7.1

## Details
Integer Overflow or Wraparound vulnerability in apr_encode functions of Apache Portable Runtime (APR) allows an attacker to write beyond bounds of a buffer.
This issue affects Apache Portable Runtime (APR) version 1.7.0.

## References
- https://lists.apache.org/thread/fw9p6sdncwsjkstwc066vz57xqzfksq9
- https://security.netapp.com/advisory/ntap-20230908-0008/
- https://nvd.nist.gov/vuln/detail/CVE-2022-24963
