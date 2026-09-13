# [H] ALPINE-CVE-2019-13391

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-13391
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13391
Type: osv

## Affected
- Alpine:v3.10: `imagemagick` — affected >=0 <6.9.10.53-r0
- Alpine:v3.8: `imagemagick` — affected >=0 <6.9.10.53-r0
- Alpine:v3.9: `imagemagick` — affected >=0 <6.9.10.53-r0

## Details
In ImageMagick 7.0.8-50 Q16, ComplexImages in MagickCore/fourier.c has a heap-based buffer over-read because of incorrect calls to GetCacheViewVirtualPixels.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13391
