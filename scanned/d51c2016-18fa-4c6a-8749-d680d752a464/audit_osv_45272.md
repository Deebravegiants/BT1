# [M] processCropSelections in `tools/tiffcrop.c` in LibTIFF through 4.5.0 has a heap-based buffer...

## Summary
Severity: Medium
Advisory: JLSEC-2025-289
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-289
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
processCropSelections in `tools/tiffcrop.c` in LibTIFF through 4.5.0 has a heap-based buffer overflow (e.g., "WRITE of size 307203") via a crafted TIFF image.

## References
- https://gitlab.com/libtiff/libtiff/-/commit/d1b6b9c1b3cae2d9e37754506c1ad8f4f7b646b5
- https://gitlab.com/libtiff/libtiff/-/issues/488
- https://lists.debian.org/debian-lts-announce/2023/01/msg00037.html
- https://security.gentoo.org/glsa/202305-31
- https://security.netapp.com/advisory/ntap-20230302-0004/
- https://www.debian.org/security/2023/dsa-5333
