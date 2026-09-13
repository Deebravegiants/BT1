# [H] CVE-2018-14946

## Summary
Severity: High
Advisory: CVE-2018-14946
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-05
Source: https://osv.dev/vulnerability/CVE-2018-14946
Type: osv

## Details
An issue has been found in PDF2JSON 0.69. The HtmlString class in ImgOutputDev.cc has Mismatched Memory Management Routines (malloc versus operator delete).

## References
- https://github.com/flexpaper/pdf2json/issues/19
- https://github.com/fouzhe/security/tree/master/pdf2json#alloc_dealloc_mismatch-in-function-htmlstring
