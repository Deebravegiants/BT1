# [M] LibTIFF 4.4.0 has an out-of-bounds read in extractImageSection in `tools/tiffcrop.c:6905`, allowing...

## Summary
Severity: Medium
Advisory: JLSEC-2025-279
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-279
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
LibTIFF 4.4.0 has an out-of-bounds read in extractImageSection in `tools/tiffcrop.c:6905`, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 48d6ece8.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2953.json
- https://gitlab.com/libtiff/libtiff/-/commit/48d6ece8389b01129e7d357f0985c8f938ce3da3
- https://gitlab.com/libtiff/libtiff/-/issues/414
- https://security.netapp.com/advisory/ntap-20221014-0008/
- https://www.debian.org/security/2023/dsa-5333
