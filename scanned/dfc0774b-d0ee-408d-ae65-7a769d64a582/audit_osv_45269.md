# [M] LibTIFF 4.4.0 has an out-of-bounds read in writeSingleSection in `tools/tiffcrop.c:7345`, allowing...

## Summary
Severity: Medium
Advisory: JLSEC-2025-285
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-285
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
LibTIFF 4.4.0 has an out-of-bounds read in writeSingleSection in `tools/tiffcrop.c:7345`, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit e8131125.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3599.json
- https://gitlab.com/libtiff/libtiff/-/commit/e813112545942107551433d61afd16ac094ff246
- https://gitlab.com/libtiff/libtiff/-/issues/398
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
- https://security.netapp.com/advisory/ntap-20230110-0001/
- https://www.debian.org/security/2023/dsa-5333
