# [M] CVE-2017-13059

## Summary
Severity: Medium
Advisory: CVE-2017-13059
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-22
Source: https://osv.dev/vulnerability/CVE-2017-13059
Type: osv

## Details
In ImageMagick 7.0.6-6, a memory leak vulnerability was found in the function WriteOneJNGImage in coders/png.c, which allows attackers to cause a denial of service (WriteJNGImage memory consumption) via a crafted file.

## References
- http://www.securityfocus.com/bid/100457
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/667
- https://security.gentoo.org/glsa/201711-07
