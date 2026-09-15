# [H] ALPINE-CVE-2025-49506

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-49506
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-49506
Type: osv

## Affected
- Alpine:v3.21: `apr-util` — affected >=1.2.0 <1.6.4-r0
- Alpine:v3.22: `apr-util` — affected >=1.2.0 <1.6.4-r0
- Alpine:v3.23: `apr-util` — affected >=1.2.0 <1.6.4-r0
- Alpine:v3.24: `apr-util` — affected >=1.2.0 <1.6.4-r0

## Details
APR-util versions 1.6.3 (and earlier) function apr_password_validate() was not constant-time with regards to hashes or passwords comparisons, potentially leaking their content via a side channel timing attack particularly on platforms without crypt() such as  Windows, BeOS, NetWare, or Android.

Users are recommended to upgrade to version 1.6.4, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-49506
