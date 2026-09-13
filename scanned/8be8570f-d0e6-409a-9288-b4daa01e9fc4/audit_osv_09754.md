# [M] CVE-2017-11352

## Summary
Severity: Medium
Advisory: CVE-2017-11352
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-11352
Type: osv

## Details
In ImageMagick before 7.0.5-10, a crafted RLE image can trigger a crash because of incorrect EOF handling in coders/rle.c. NOTE: this vulnerability exists because of an incomplete fix for CVE-2017-9144.

## References
- http://www.securityfocus.com/bid/99600
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4040
- https://bugs.debian.org/868469
- https://github.com/ImageMagick/ImageMagick/issues/502
