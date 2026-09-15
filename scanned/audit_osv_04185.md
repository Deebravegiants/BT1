# [M] Apache Portable Runtime (APR): Unexpected lax shared memory permissions

## Summary
Severity: Medium
Advisory: BIT-apr-2023-49582
Aliases: CVE-2023-49582
Ecosystem: Bitnami
Published: 2024-08-28
Source: https://osv.dev/vulnerability/BIT-apr-2023-49582
Type: osv

## Affected
- Bitnami: `apr` — affected >=0.9.0 <1.7.5

## Details
Lax permissions set by the Apache Portable Runtime library on Unix platforms would allow local users read access to named shared memory segments, potentially revealing sensitive application data. 

This issue does not affect non-Unix platforms, or builds with APR_USE_SHMEM_SHMGET=1 (apr.h)

Users are recommended to upgrade to APR version 1.7.5, which fixes this issue.

## References
- https://lists.apache.org/thread/sntjc04t1rvjhdzz2tzmtz2zdnmv7dc4
- http://www.openwall.com/lists/oss-security/2024/08/26/1
- https://security.netapp.com/advisory/ntap-20241101-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2023-49582
