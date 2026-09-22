# [C] ALPINE-CVE-2019-14697

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-14697
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14697
Type: osv

## Affected
- Alpine:v3.10: `musl` — affected >=0.9.12 <1.1.22-r3
- Alpine:v3.11: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.12: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.13: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.14: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.15: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.16: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.17: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.18: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.19: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.20: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.21: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.22: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.23: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.24: `musl` — affected >=0.9.12 <1.1.23-r2
- Alpine:v3.7: `musl` — affected >=0.9.12 <1.1.18-r4
- Alpine:v3.8: `musl` — affected >=0.9.12 <1.1.19-r11
- Alpine:v3.9: `musl` — affected >=0.9.12 <1.1.20-r5

## Details
musl libc through 1.1.23 has an x87 floating-point stack adjustment imbalance, related to the math/i386/ directory. In some cases, use of this library could introduce out-of-bounds writes that are not present in an application's source code.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14697
