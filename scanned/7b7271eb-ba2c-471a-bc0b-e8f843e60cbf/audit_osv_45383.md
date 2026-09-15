# [M] JLSEC-2026-1105

## Summary
Severity: Medium
Advisory: JLSEC-2026-1105
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1105
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
In LibRaw, an out-of-bounds read vulnerability exists within the "`LibRaw::adobe_copy_pixel()`" function (`libraw\src\decoders\dng.cpp`) when reading data from the image file.

## References
- https://github.com/LibRaw/LibRaw/commit/a6937d4046a7c4742b683a04c8564605fd9be4fb
- https://github.com/LibRaw/LibRaw/commit/a6937d4046a7c4742b683a04c8564605fd9be4fb
- https://github.com/LibRaw/LibRaw/issues/273
- https://github.com/LibRaw/LibRaw/issues/273
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
