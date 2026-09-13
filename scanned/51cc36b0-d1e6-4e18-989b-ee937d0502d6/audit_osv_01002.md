# [H] ALPINE-CVE-2018-14883

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-14883
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14883
Type: osv

## Affected
- Alpine:v3.5: `php5` — affected >=0 <5.6.37-r0

## Details
An issue was discovered in PHP before 5.6.37, 7.0.x before 7.0.31, 7.1.x before 7.1.20, and 7.2.x before 7.2.8. An Integer Overflow leads to a heap-based buffer over-read in exif_thumbnail_extract of exif.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14883
