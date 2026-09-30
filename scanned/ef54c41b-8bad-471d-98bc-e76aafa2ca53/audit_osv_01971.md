# [H] ALPINE-CVE-2020-35524

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-35524
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-35524
Type: osv

## Affected
- Alpine:v3.13: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.14: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.15: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.16: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.17: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.18: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.19: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.20: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.21: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.22: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.23: `tiff` — affected >=0 <4.2.0-r0
- Alpine:v3.24: `tiff` — affected >=0 <4.2.0-r0

## Details
A heap-based buffer overflow flaw was found in libtiff in the handling of TIFF images in libtiff's TIFF2PDF tool. A specially crafted TIFF file can lead to arbitrary code execution. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-35524
