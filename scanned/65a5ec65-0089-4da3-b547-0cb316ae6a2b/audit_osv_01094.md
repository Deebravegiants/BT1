# [H] ALPINE-CVE-2018-19931

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-19931
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19931
Type: osv

## Affected
- Alpine:v3.10: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.11: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.12: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.13: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.14: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.15: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.16: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.17: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.18: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.19: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.20: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.21: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.22: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.23: `binutils` — affected >=0 <2.32-r0
- Alpine:v3.24: `binutils` — affected >=0 <2.32-r0

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils through 2.31. There is a heap-based buffer overflow in bfd_elf32_swap_phdr_in in elfcode.h because the number of program headers is not restricted.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19931
