# [H] ALPINE-CVE-2019-10650

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-10650
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10650
Type: osv

## Affected
- Alpine:v3.10: `imagemagick` — affected >=0 <7.0.8.38-r0
- Alpine:v3.8: `imagemagick` — affected >=0 <7.0.8.38-r0
- Alpine:v3.9: `imagemagick` — affected >=0 <7.0.8.38-r0

## Details
In ImageMagick 7.0.8-36 Q16, there is a heap-based buffer over-read in the function WriteTIFFImage of coders/tiff.c, which allows an attacker to cause a denial of service or information disclosure via a crafted image file.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10650
