# [M] ALPINE-CVE-2018-14498

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-14498
Ecosystem: Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-03-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14498
Type: osv

## Affected
- Alpine:v3.7: `libjpeg-turbo` — affected >=0 <1.5.3-r3
- Alpine:v3.8: `libjpeg-turbo` — affected >=0 <1.5.3-r5
- Alpine:v3.9: `libjpeg-turbo` — affected >=0 <1.5.3-r5

## Details
get_8bit_row in rdbmp.c in libjpeg-turbo through 1.5.90 and MozJPEG through 3.3.1 allows attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted 8-bit BMP in which one or more of the color indices is out of range for the number of palette entries.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14498
