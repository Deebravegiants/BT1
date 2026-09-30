# [C] ALPINE-CVE-2022-28331

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-28331
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-28331
Type: osv

## Affected
- Alpine:v3.14: `apr` — affected >=0 <1.7.1-r0
- Alpine:v3.15: `apr` — affected >=0 <1.7.1-r0
- Alpine:v3.16: `apr` — affected >=0 <1.7.1-r0
- Alpine:v3.17: `apr` — affected >=0 <1.7.1-r0
- Alpine:v3.18: `apr` — affected >=0 <1.7.1-r0
- Alpine:v3.19: `apr` — affected >=0 <1.7.1-r0
- Alpine:v3.20: `apr` — affected >=0 <1.7.1-r0
- Alpine:v3.21: `apr` — affected >=0 <1.7.1-r0
- Alpine:v3.22: `apr` — affected >=0 <1.7.1-r0
- Alpine:v3.23: `apr` — affected >=0 <1.7.1-r0
- Alpine:v3.24: `apr` — affected >=0 <1.7.1-r0

## Details
On Windows, Apache Portable Runtime 1.7.0 and earlier may write beyond the end of a stack based buffer in apr_socket_sendv(). This is a result of integer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-28331
