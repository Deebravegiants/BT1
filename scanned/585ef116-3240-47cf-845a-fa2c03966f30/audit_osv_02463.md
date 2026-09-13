# [C] ALPINE-CVE-2022-24963

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-24963
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24963
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
Integer Overflow or Wraparound vulnerability in apr_encode functions of Apache Portable Runtime (APR) allows an attacker to write beyond bounds of a buffer.
This issue affects Apache Portable Runtime (APR) version 1.7.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24963
