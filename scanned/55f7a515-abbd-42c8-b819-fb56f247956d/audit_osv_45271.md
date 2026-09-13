# [H] A vulnerability was found in LibTIFF

## Summary
Severity: High
Advisory: JLSEC-2025-288
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-288
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
A vulnerability was found in LibTIFF. It has been classified as critical. This affects the function TIFFReadRGBATileExt of the file `libtiff/tif_getimage.c`. The manipulation leads to integer overflow. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. The name of the patch is 227500897dfb07fb7d27f7aa570050e62617e3be. It is recommended to apply a patch to fix this issue. The identifier VDB-213549 was assigned to this vulnerability.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=53137
- https://gitlab.com/libtiff/libtiff/-/commit/227500897dfb07fb7d27f7aa570050e62617e3be
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
- https://oss-fuzz.com/download?testcase_id=5738253143900160
- https://security.netapp.com/advisory/ntap-20221215-0009/
- https://support.apple.com/kb/HT213841
- https://support.apple.com/kb/HT213843
- https://vuldb.com/?id.213549
