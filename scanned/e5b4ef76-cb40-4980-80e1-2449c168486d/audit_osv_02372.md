# [H] ALPINE-CVE-2022-0891

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-0891
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-0891
Type: osv

## Affected
- Alpine:v3.13: `tiff` — affected >=0 <4.3.0-r0
- Alpine:v3.14: `tiff` — affected >=0 <4.3.0-r0
- Alpine:v3.15: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.16: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.17: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.18: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.19: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.20: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.21: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.22: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.23: `tiff` — affected >=0 <4.3.0-r1
- Alpine:v3.24: `tiff` — affected >=0 <4.3.0-r1

## Details
A heap buffer overflow in ExtractImageSection function in tiffcrop.c in libtiff library Version 4.3.0 allows attacker to trigger unsafe or out of bounds memory access via crafted TIFF image file which could result into application crash, potential information disclosure or any other context-dependent impact

## References
- https://security.alpinelinux.org/vuln/CVE-2022-0891
