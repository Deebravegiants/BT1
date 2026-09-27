# [M] ALPINE-CVE-2016-5010

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-5010
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5010
Type: osv

## Affected
- Alpine:v3.2: `imagemagick` — affected >=0 <6.9.6.8-r0
- Alpine:v3.3: `imagemagick` — affected >=0 <6.9.6.8-r0
- Alpine:v3.4: `imagemagick` — affected >=0 <6.9.5.3

## Details
coders/tiff.c in ImageMagick before 6.9.5-3 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TIFF file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5010
