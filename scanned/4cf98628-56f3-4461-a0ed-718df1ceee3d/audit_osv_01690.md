# [H] ALPINE-CVE-2019-9956

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-9956
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9956
Type: osv

## Affected
- Alpine:v3.10: `imagemagick` — affected >=0 <7.0.8.38-r0
- Alpine:v3.8: `imagemagick` — affected >=0 <7.0.8.38-r0
- Alpine:v3.9: `imagemagick` — affected >=0 <7.0.8.38-r0

## Details
In ImageMagick 7.0.8-35 Q16, there is a stack-based buffer overflow in the function PopHexPixel of coders/ps.c, which allows an attacker to cause a denial of service or code execution via a crafted image file.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9956
