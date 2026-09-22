# [M] ALPINE-CVE-2022-34526

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-34526
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-07-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-34526
Type: osv

## Affected
- Alpine:v3.15: `tiff` — affected >=0 <4.4.0-r3
- Alpine:v3.16: `tiff` — affected >=0 <4.4.0-r3
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.18: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.19: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.20: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.21: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.22: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.23: `tiff` — affected >=0 <4.4.0-r1
- Alpine:v3.24: `tiff` — affected >=0 <4.4.0-r1

## Details
A stack overflow was discovered in the _TIFFVGetField function of Tiffsplit v4.4.0. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted TIFF file parsed by the "tiffsplit" or "tiffcrop" utilities.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-34526
