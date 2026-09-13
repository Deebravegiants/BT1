# [M] ALPINE-CVE-2018-20002

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-20002
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20002
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
The _bfd_generic_read_minisymbols function in syms.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.31, has a memory leak via a crafted ELF file, leading to a denial of service (memory consumption), as demonstrated by nm.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20002
