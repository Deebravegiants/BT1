# [M] ALPINE-CVE-2019-12904

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-12904
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12904
Type: osv

## Affected
- Alpine:v3.10: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.11: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.12: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.13: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.14: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.15: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.16: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.17: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.18: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.19: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.20: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.21: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.22: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.23: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.24: `libgcrypt` — affected >=0 <1.8.4-r2
- Alpine:v3.7: `libgcrypt` — affected >=0 <1.8.3-r1
- Alpine:v3.8: `libgcrypt` — affected >=0 <1.8.3-r1
- Alpine:v3.9: `libgcrypt` — affected >=0 <1.8.4-r1

## Details
In Libgcrypt 1.8.4, the C implementation of AES is vulnerable to a flush-and-reload side-channel attack because physical addresses are available to other processes. (The C implementation is used on platforms where an assembly-language implementation is unavailable.) NOTE: the vendor's position is that the issue report cannot be validated because there is no description of an attack

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12904
