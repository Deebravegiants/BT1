# [M] ALPINE-CVE-2022-25147

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-25147
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2023-01-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-25147
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
- Alpine:v3.14: `apr-util` — affected >=0 <1.6.3-r0
- Alpine:v3.15: `apr-util` — affected >=0 <1.6.3-r0
- Alpine:v3.16: `apr-util` — affected >=0 <1.6.3-r0
- Alpine:v3.17: `apr-util` — affected >=0 <1.6.3-r0
- Alpine:v3.18: `apr-util` — affected >=0 <1.6.3-r0
- Alpine:v3.19: `apr-util` — affected >=0 <1.6.3-r0
- Alpine:v3.20: `apr-util` — affected >=0 <1.6.3-r0
- Alpine:v3.21: `apr-util` — affected >=0 <1.6.3-r0
- Alpine:v3.22: `apr-util` — affected >=0 <1.6.3-r0
- Alpine:v3.23: `apr-util` — affected >=0 <1.6.3-r0
- Alpine:v3.24: `apr-util` — affected >=0 <1.6.3-r0

## Details
Integer Overflow or Wraparound vulnerability in apr_base64 functions of Apache Portable Runtime Utility (APR-util) allows an attacker to write beyond bounds of a buffer.




This issue affects Apache Portable Runtime Utility (APR-util) 1.6.1 and prior versions.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-25147
