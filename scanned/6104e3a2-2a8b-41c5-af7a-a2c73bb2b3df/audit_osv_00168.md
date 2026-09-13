# [H] ALPINE-CVE-2016-6491

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6491
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6491
Type: osv

## Affected
- Alpine:v3.2: `imagemagick` — affected >=0 <6.9.6.8-r0
- Alpine:v3.3: `imagemagick` — affected >=0 <6.9.6.8-r0
- Alpine:v3.4: `imagemagick` — affected >=0 <6.9.5.3

## Details
Buffer overflow in the Get8BIMProperty function in MagickCore/property.c in ImageMagick before 6.9.5-4 and 7.x before 7.0.2-6 allows remote attackers to cause a denial of service (out-of-bounds read, memory leak, and crash) via a crafted image.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6491
