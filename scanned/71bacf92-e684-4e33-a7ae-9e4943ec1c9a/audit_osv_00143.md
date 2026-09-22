# [H] ALPINE-CVE-2016-5842

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-5842
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5842
Type: osv

## Affected
- Alpine:v3.2: `imagemagick` — affected >=7.0.0-0 <6.9.6.8-r0
- Alpine:v3.3: `imagemagick` — affected >=7.0.0-0 <6.9.6.8-r0
- Alpine:v3.4: `imagemagick` — affected >=7.0.0-0 <6.9.5.3

## Details
MagickCore/property.c in ImageMagick before 7.0.2-1 allows remote attackers to obtain sensitive memory information via vectors involving the q variable, which triggers an out-of-bounds read.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5842
