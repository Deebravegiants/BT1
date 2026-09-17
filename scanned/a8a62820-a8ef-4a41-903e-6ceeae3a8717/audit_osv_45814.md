# [M] JLSEC-2026-360

## Summary
Severity: Medium
Advisory: JLSEC-2026-360
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/JLSEC-2026-360
Type: osv

## Affected
- Julia: `LibGD_jll` — affected >=0 <2.3.3+0

## Details
`read_header_tga` in `gd_tga.c` in the GD Graphics Library (aka LibGD) through 2.3.2 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TGA file.

## References
- https://github.com/libgd/libgd/issues/697
- https://github.com/libgd/libgd/pull/711/commits/8b111b2b4a4842179be66db68d84dda91a246032
- https://lists.debian.org/debian-lts-announce/2024/04/msg00003.html
