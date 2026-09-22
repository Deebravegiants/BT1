# [M] LibTIFF 4.3.0 has an out-of-bounds read in `_TIFFmemcpy` in `tif_unix.c` in certain situations...

## Summary
Severity: Medium
Advisory: JLSEC-2025-259
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-259
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=4.3.0+0 <4.4.0+0

## Details
LibTIFF 4.3.0 has an out-of-bounds read in `_TIFFmemcpy` in `tif_unix.c` in certain situations involving a custom tag and 0x0200 as the second word of the DE field.

## References
- https://gitlab.com/libtiff/libtiff/-/issues/355
- https://gitlab.com/libtiff/libtiff/-/merge_requests/287
- https://lists.debian.org/debian-lts-announce/2022/03/msg00001.html
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20220311-0002/
- https://www.debian.org/security/2022/dsa-5108
