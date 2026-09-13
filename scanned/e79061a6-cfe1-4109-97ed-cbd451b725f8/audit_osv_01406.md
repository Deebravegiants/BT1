# [M] ALPINE-CVE-2019-13296

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-13296
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13296
Type: osv

## Affected
- Alpine:v3.10: `imagemagick` — affected >=0 <6.9.10.53-r0
- Alpine:v3.8: `imagemagick` — affected >=0 <6.9.10.53-r0
- Alpine:v3.9: `imagemagick` — affected >=0 <6.9.10.53-r0

## Details
ImageMagick 7.0.8-50 Q16 has direct memory leaks in AcquireMagickMemory because of an error in CLIListOperatorImages in MagickWand/operation.c for a NULL value.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13296
