# [M] CVE-2017-13060

## Summary
Severity: Medium
Advisory: CVE-2017-13060
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-22
Source: https://osv.dev/vulnerability/CVE-2017-13060
Type: osv

## Details
In ImageMagick 7.0.6-5, a memory leak vulnerability was found in the function ReadMATImage in coders/mat.c, which allows attackers to cause a denial of service via a crafted file.

## References
- http://www.securityfocus.com/bid/100469
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/644
- https://security.gentoo.org/glsa/201711-07
