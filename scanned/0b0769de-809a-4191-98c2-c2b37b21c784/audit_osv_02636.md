# [H] ALPINE-CVE-2022-3970

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-3970
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3970
Type: osv

## Affected
- Alpine:v3.14: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.15: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.16: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r2
- Alpine:v3.18: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.19: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.20: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.21: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.22: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.23: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.24: `tiff` — affected >=0 <4.5.0-r0

## Details
A vulnerability was found in LibTIFF. It has been classified as critical. This affects the function TIFFReadRGBATileExt of the file libtiff/tif_getimage.c. The manipulation leads to integer overflow. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. The name of the patch is 227500897dfb07fb7d27f7aa570050e62617e3be. It is recommended to apply a patch to fix this issue. The identifier VDB-213549 was assigned to this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3970
