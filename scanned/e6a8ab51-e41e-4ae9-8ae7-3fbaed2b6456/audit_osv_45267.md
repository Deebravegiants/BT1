# [M] LibTIFF 4.4.0 has an out-of-bounds write in `_TIFFmemcpy` in `libtiff/tif_unix.c:346` when called...

## Summary
Severity: Medium
Advisory: JLSEC-2025-283
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-283
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
LibTIFF 4.4.0 has an out-of-bounds write in `_TIFFmemcpy` in `libtiff/tif_unix.c:346` when called from extractImageSection, `tools/tiffcrop.c:6826`, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 236b7191.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3597.json
- https://gitlab.com/libtiff/libtiff/-/commit/236b7191f04c60d09ee836ae13b50f812c841047
- https://gitlab.com/libtiff/libtiff/-/issues/413
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
- https://security.netapp.com/advisory/ntap-20230110-0001/
- https://www.debian.org/security/2023/dsa-5333
