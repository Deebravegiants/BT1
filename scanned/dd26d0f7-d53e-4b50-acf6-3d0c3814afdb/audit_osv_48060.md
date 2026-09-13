# [M] CVE-2017-17681

## Summary
Severity: Medium
Advisory: CVE-2017-17681
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17681
Type: osv

## Details
In ImageMagick 7.0.7-12 Q16, an infinite loop vulnerability was found in the function ReadPSDChannelZip in coders/psd.c, which allows attackers to cause a denial of service (CPU exhaustion) via a crafted psd image file.

## References
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- http://www.securityfocus.com/bid/102206
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/869
