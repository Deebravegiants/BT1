# [M] ALPINE-CVE-2019-11472

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-11472
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11472
Type: osv

## Affected
- Alpine:v3.10: `imagemagick` — affected >=0 <7.0.8.44-r0
- Alpine:v3.8: `imagemagick` — affected >=0 <7.0.8.44-r0
- Alpine:v3.9: `imagemagick` — affected >=0 <7.0.8.44-r0

## Details
ReadXWDImage in coders/xwd.c in the XWD image parsing component of ImageMagick 7.0.8-41 Q16 allows attackers to cause a denial-of-service (divide-by-zero error) by crafting an XWD image file in which the header indicates neither LSB first nor MSB first.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11472
