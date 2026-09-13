# [M] JLSEC-2026-1103

## Summary
Severity: Medium
Advisory: JLSEC-2026-1103
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1103
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
In LibRaw, an out-of-bounds read vulnerability exists within the `get_huffman_diff()` function (`libraw\src\x3f\x3f_utils_patched.cpp`) when reading data from an image file.

## References
- https://github.com/LibRaw/LibRaw/commit/d75af00681a74dcc8b929207eb895611a6eceb68
- https://github.com/LibRaw/LibRaw/commit/d75af00681a74dcc8b929207eb895611a6eceb68
- https://github.com/LibRaw/LibRaw/issues/270
- https://github.com/LibRaw/LibRaw/issues/270
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
