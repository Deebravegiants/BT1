# [M] ALPINE-CVE-2019-10649

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-10649
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10649
Type: osv

## Affected
- Alpine:v3.10: `imagemagick` — affected >=0 <7.0.8.38-r0
- Alpine:v3.8: `imagemagick` — affected >=0 <7.0.8.38-r0
- Alpine:v3.9: `imagemagick` — affected >=0 <7.0.8.38-r0

## Details
In ImageMagick 7.0.8-36 Q16, there is a memory leak in the function SVGKeyValuePairs of coders/svg.c, which allows an attacker to cause a denial of service via a crafted image file.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10649
