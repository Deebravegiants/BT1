# [M] JLSEC-2026-1102

## Summary
Severity: Medium
Advisory: JLSEC-2026-1102
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1102
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
In LibRaw, there is an out-of-bounds write vulnerability within the "`new_node()`" function (`libraw\src\x3f\x3f_utils_patched.cpp`) that can be triggered via a crafted X3F file.

## References
- https://github.com/LibRaw/LibRaw/commit/11c4db253ef2c9bb44247b578f5caa57c66a1eeb
- https://github.com/LibRaw/LibRaw/commit/11c4db253ef2c9bb44247b578f5caa57c66a1eeb
- https://github.com/LibRaw/LibRaw/issues/272
- https://github.com/LibRaw/LibRaw/issues/272
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
