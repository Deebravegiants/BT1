# [C] ALPINE-CVE-2017-5225

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-5225
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5225
Type: osv

## Affected
- Alpine:v3.10: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.11: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.12: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.13: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.14: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.15: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.16: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.17: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.18: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.19: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.20: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.21: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.22: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.23: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.24: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.5: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.6: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.7: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.8: `tiff` — affected >=0 <4.0.7-r1
- Alpine:v3.9: `tiff` — affected >=0 <4.0.7-r1

## Details
LibTIFF version 4.0.7 is vulnerable to a heap buffer overflow in the tools/tiffcp resulting in DoS or code execution via a crafted BitsPerSample value.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5225
