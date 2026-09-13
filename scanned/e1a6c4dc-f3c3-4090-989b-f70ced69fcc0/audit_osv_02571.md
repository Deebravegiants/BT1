# [M] ALPINE-CVE-2022-3213

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-3213
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3213
Type: osv

## Affected
- Alpine:v3.18: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.19: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.20: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.21: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.22: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.23: `tiff` — affected >=0 <4.5.0-r0
- Alpine:v3.24: `tiff` — affected >=0 <4.5.0-r0

## Details
A heap buffer overflow issue was found in ImageMagick. When an application processes a malformed TIFF file, it could lead to undefined behavior or a crash causing a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3213
