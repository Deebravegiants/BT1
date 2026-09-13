# [H] Apache Portable Runtime Utility: apr_password_validate() vulnerable to timing attack

## Summary
Severity: High
Advisory: BIT-apr-util-2025-49506
Aliases: CVE-2025-49506
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-apr-util-2025-49506
Type: osv

## Affected
- Bitnami: `apr-util` — affected >=1.2.0 <1.6.4

## Details
APR-util versions 1.6.3 (and earlier) function apr_password_validate() was not constant-time with regards to hashes or passwords comparisons, potentially leaking their content via a side channel timing attack particularly on platforms without crypt() such as  Windows, BeOS, NetWare, or Android.

Users are recommended to upgrade to version 1.6.4, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/8
- https://lists.apache.org/thread/2v8o3bj9pb7lfcr57bdnjg9xfkj04mg5
- https://nvd.nist.gov/vuln/detail/CVE-2025-49506
