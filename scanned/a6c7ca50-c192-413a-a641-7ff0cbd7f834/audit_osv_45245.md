# [H] `tif_getimage.c` in LibTIFF through 4.0.10, as used in GDAL through 3.0.1 and other products, has an...

## Summary
Severity: High
Advisory: JLSEC-2025-254
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-254
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.1.0+0

## Details
`tif_getimage.c` in LibTIFF through 4.0.10, as used in GDAL through 3.0.1 and other products, has an integer overflow that potentially causes a heap-based buffer overflow via a crafted RGBA image, related to a "Negative-size-param" condition.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=16443
- https://github.com/OSGeo/gdal/commit/21674033ee246f698887604c7af7ba1962a40ddf
- https://gitlab.com/libtiff/libtiff/commit/4bb584a35f87af42d6cf09d15e9ce8909a839145
- https://lists.debian.org/debian-lts-announce/2019/11/msg00027.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LM5ZW7E3IEW7LT2BPJP7D3RN6OUOE3MX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M3S4WNIMZ7XSLY2LD5FPRPZMGNUBVKOG/
- https://seclists.org/bugtraq/2020/Jan/32
- https://security.gentoo.org/glsa/202003-25
- https://security.netapp.com/advisory/ntap-20241220-0007/
- https://www.debian.org/security/2020/dsa-4608
- https://www.debian.org/security/2020/dsa-4670
