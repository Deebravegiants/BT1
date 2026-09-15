# [H] ALPINE-CVE-2019-13135

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-13135
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13135
Type: osv

## Affected
- Alpine:v3.10: `imagemagick` — affected >=7.0.0-0 <6.9.10.53-r0
- Alpine:v3.8: `imagemagick` — affected >=7.0.0-0 <6.9.10.53-r0
- Alpine:v3.9: `imagemagick` — affected >=7.0.0-0 <6.9.10.53-r0

## Details
ImageMagick before 7.0.8-50 has a "use of uninitialized value" vulnerability in the function ReadCUTImage in coders/cut.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13135
