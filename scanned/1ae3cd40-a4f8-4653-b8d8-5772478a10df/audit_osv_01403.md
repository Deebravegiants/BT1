# [H] ALPINE-CVE-2019-13136

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-13136
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13136
Type: osv

## Affected
- Alpine:v3.10: `imagemagick` — affected >=0 <6.9.10.53-r0
- Alpine:v3.8: `imagemagick` — affected >=0 <6.9.10.53-r0
- Alpine:v3.9: `imagemagick` — affected >=0 <6.9.10.53-r0

## Details
ImageMagick before 7.0.8-50 has an integer overflow vulnerability in the function TIFFSeekCustomStream in coders/tiff.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13136
