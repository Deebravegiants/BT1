# [M] CVE-2018-11656

## Summary
Severity: Medium
Advisory: CVE-2018-11656
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-06-01
Source: https://osv.dev/vulnerability/CVE-2018-11656
Type: osv

## Details
In ImageMagick 7.0.7-20 Q16 x86_64, a memory leak vulnerability was found in the function ReadDCMImage in coders/dcm.c, which allows attackers to cause a denial of service via a crafted DCM image file.

## References
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/931
