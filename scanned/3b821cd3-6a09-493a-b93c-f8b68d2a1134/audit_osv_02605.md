# [M] ALPINE-CVE-2022-3570

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-3570
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3570
Type: osv

## Affected
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r2
- Alpine:v3.18: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.19: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.20: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.21: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.22: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.23: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.24: `tiff` — affected >=0 <4.5.0-r0

## Details
Multiple heap buffer overflows in tiffcrop.c utility in libtiff library Version 4.4.0 allows attacker to trigger unsafe or out of bounds memory access via crafted TIFF image file which could result into application crash, potential information disclosure or any other context-dependent impact

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3570
