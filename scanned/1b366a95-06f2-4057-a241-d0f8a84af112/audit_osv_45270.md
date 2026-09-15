# [M] LibTIFF 4.4.0 has an out-of-bounds write in `_TIFFmemset` in `libtiff/tif_unix.c:340` when called...

## Summary
Severity: Medium
Advisory: JLSEC-2025-286
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-286
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
LibTIFF 4.4.0 has an out-of-bounds write in `_TIFFmemset` in `libtiff/tif_unix.c:340` when called from processCropSelections, `tools/tiffcrop.c:7619`, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 236b7191.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3626.json
- https://gitlab.com/libtiff/libtiff/-/commit/236b7191f04c60d09ee836ae13b50f812c841047
- https://gitlab.com/libtiff/libtiff/-/issues/426
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
- https://security.netapp.com/advisory/ntap-20230110-0001/
