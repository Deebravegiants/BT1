# [C] Apache Portable Runtime (APR):  Windows out-of-bounds write in apr_socket_sendv function

## Summary
Severity: Critical
Advisory: BIT-apr-2022-28331
Aliases: CVE-2022-28331
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apr-2022-28331
Type: osv

## Affected
- Bitnami: `apr` — affected >=0 <1.7.1

## Details
On Windows, Apache Portable Runtime 1.7.0 and earlier may write beyond the end of a stack based buffer in apr_socket_sendv(). This is a result of integer overflow.

## References
- https://lists.apache.org/thread/5pfdfn7h0vsdo5xzjn97vghp0x42jj2r
- https://nvd.nist.gov/vuln/detail/CVE-2022-28331
