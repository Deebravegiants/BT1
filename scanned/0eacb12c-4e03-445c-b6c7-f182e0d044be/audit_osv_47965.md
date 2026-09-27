# [H] CVE-2017-15601

## Summary
Severity: High
Advisory: CVE-2017-15601
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2017-15601
Type: osv

## Details
In GNU Libextractor 1.4, there is a heap-based buffer overflow in the EXTRACTOR_png_extract_method function in plugins/png_extractor.c, related to processiTXt and stndup.

## References
- https://ftp.gnu.org/gnu/libextractor/libextractor-1.6.tar.gz
- https://lists.debian.org/debian-lts-announce/2017/12/msg00000.html
- http://lists.gnu.org/archive/html/bug-libextractor/2017-10/msg00006.html
