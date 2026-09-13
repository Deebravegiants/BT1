# [H] CVE-2019-13568

## Summary
Severity: High
Advisory: CVE-2019-13568
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-13568
Type: osv

## Details
CImg through 2.6.7 has a heap-based buffer overflow in _load_bmp in CImg.h because of erroneous memory allocation for a malformed BMP image.

## References
- http://cimg.eu/
- https://github.com/dtschump/CImg/commit/ac8003393569aba51048c9d67e1491559877b1d1
- https://github.com/dtschump/CImg
