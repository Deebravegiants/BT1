# [M] CVE-2021-40985

## Summary
Severity: Medium
Advisory: CVE-2021-40985
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-11-03
Source: https://osv.dev/vulnerability/CVE-2021-40985
Type: osv

## Details
A stack-based buffer under-read in htmldoc before 1.9.12, allows attackers to cause a denial of service via a crafted BMP image to image_load_bmp.

## References
- https://lists.debian.org/debian-lts-announce/2022/02/msg00022.html
- https://github.com/michaelrsweet/htmldoc/commit/f12b9666e582a8e7b70f11b28e5ffc49ad625d43
- https://github.com/michaelrsweet/htmldoc/issues/444
