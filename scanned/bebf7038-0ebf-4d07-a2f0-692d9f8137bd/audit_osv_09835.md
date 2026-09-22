# [M] CVE-2017-11640

## Summary
Severity: Medium
Advisory: CVE-2017-11640
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-11640
Type: osv

## Details
When ImageMagick 7.0.6-1 processes a crafted file in convert, it can lead to an address access exception in the WritePTIFImage() function in coders/tiff.c.

## References
- https://usn.ubuntu.com/3681-1/
- http://www.securityfocus.com/bid/99989
- https://security.gentoo.org/glsa/201711-07
- https://www.debian.org/security/2017/dsa-4019
- https://www.debian.org/security/2017/dsa-4040
- https://github.com/ImageMagick/ImageMagick/issues/584
