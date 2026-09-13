# [M] ALPINE-CVE-2023-1972

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-1972
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-1972
Type: osv

## Affected
- Alpine:v3.18: `binutils` — affected >=2.35 <2.40-r7
- Alpine:v3.19: `binutils` — affected >=2.35 <2.40-r10
- Alpine:v3.20: `binutils` — affected >=2.35 <2.40-r10
- Alpine:v3.21: `binutils` — affected >=2.35 <2.40-r10
- Alpine:v3.22: `binutils` — affected >=2.35 <2.40-r10
- Alpine:v3.23: `binutils` — affected >=2.35 <2.40-r10
- Alpine:v3.24: `binutils` — affected >=2.35 <2.40-r10

## Details
A potential heap based buffer overflow was found in _bfd_elf_slurp_version_tables() in bfd/elf.c. This may lead to loss of availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-1972
