# [C] ALPINE-CVE-2016-5841

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-5841
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5841
Type: osv

## Affected
- Alpine:v3.2: `imagemagick` — affected >=0 <6.9.6.8-r0
- Alpine:v3.3: `imagemagick` — affected >=0 <6.9.6.8-r0
- Alpine:v3.4: `imagemagick` — affected >=0 <6.9.5.3

## Details
Integer overflow in MagickCore/profile.c in ImageMagick before 7.0.2-1 allows remote attackers to cause a denial of service (segmentation fault) or possibly execute arbitrary code via vectors involving the offset variable.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5841
