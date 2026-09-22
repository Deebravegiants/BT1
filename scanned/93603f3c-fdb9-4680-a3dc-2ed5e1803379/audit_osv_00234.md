# [M] ALPINE-CVE-2016-7799

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-7799
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7799
Type: osv

## Affected
- Alpine:v3.2: `imagemagick` — affected >=7.0.0-0 <6.9.6.8-r0
- Alpine:v3.3: `imagemagick` — affected >=7.0.0-0 <6.9.6.8-r0
- Alpine:v3.4: `imagemagick` — affected >=7.0.0-0 <6.9.5.9-r1

## Details
MagickCore/profile.c in ImageMagick before 7.0.3-2 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7799
