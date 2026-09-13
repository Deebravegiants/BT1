# [M] ALPINE-CVE-2022-2867

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-2867
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2867
Type: osv

## Affected
- Alpine:v3.13: `tiff` — affected >=0 <4.4.0-r0
- Alpine:v3.14: `tiff` — affected >=0 <4.4.0-r0
- Alpine:v3.15: `tiff` — affected >=0 <4.4.0-r0
- Alpine:v3.16: `tiff` — affected >=0 <4.4.0-r0
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r0
- Alpine:v3.18: `tiff` — affected >=0 <4.4.0-r0
- Alpine:v3.19: `tiff` — affected >=0 <4.4.0-r0
- Alpine:v3.20: `tiff` — affected >=0 <4.4.0-r0
- Alpine:v3.21: `tiff` — affected >=0 <4.4.0-r0
- Alpine:v3.22: `tiff` — affected >=0 <4.4.0-r0
- Alpine:v3.23: `tiff` — affected >=0 <4.4.0-r0
- Alpine:v3.24: `tiff` — affected >=0 <4.4.0-r0

## Details
libtiff's tiffcrop utility has a uint32_t underflow that can lead to out of bounds read and write. An attacker who supplies a crafted file to tiffcrop (likely via tricking a user to run tiffcrop on it with certain parameters) could cause a crash or in some cases, further exploitation.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2867
