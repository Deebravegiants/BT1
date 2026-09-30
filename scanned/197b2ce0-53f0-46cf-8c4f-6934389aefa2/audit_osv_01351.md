# [H] ALPINE-CVE-2019-11598

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-11598
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-04-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11598
Type: osv

## Affected
- Alpine:v3.10: `imagemagick` — affected >=0 <7.0.8.44-r0
- Alpine:v3.8: `imagemagick` — affected >=0 <7.0.8.44-r0
- Alpine:v3.9: `imagemagick` — affected >=0 <7.0.8.44-r0

## Details
In ImageMagick 7.0.8-40 Q16, there is a heap-based buffer over-read in the function WritePNMImage of coders/pnm.c, which allows an attacker to cause a denial of service or possibly information disclosure via a crafted image file. This is related to SetGrayscaleImage in MagickCore/quantize.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11598
