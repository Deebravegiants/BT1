# [H] CVE-2021-43579

## Summary
Severity: High
Advisory: CVE-2021-43579
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2021-43579
Type: osv

## Details
A stack-based buffer overflow in image_load_bmp() in HTMLDOC <= 1.9.13 results in remote code execution if the victim converts an HTML document linking to a crafted BMP file.

## References
- https://github.com/michaelrsweet/htmldoc/compare/v1.9.12...v1.9.13
- https://lists.debian.org/debian-lts-announce/2022/02/msg00022.html
- https://github.com/michaelrsweet/htmldoc/commit/27d08989a5a567155d506ac870ae7d8cc88fa58b
- https://github.com/michaelrsweet/htmldoc/issues/453
- https://github.com/michaelrsweet/htmldoc/issues/456
