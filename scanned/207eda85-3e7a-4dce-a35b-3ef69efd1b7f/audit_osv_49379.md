# [H] CVE-2019-11597

## Summary
Severity: High
Advisory: CVE-2019-11597
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-04-29
Source: https://osv.dev/vulnerability/CVE-2019-11597
Type: osv

## Details
In ImageMagick 7.0.8-43 Q16, there is a heap-based buffer over-read in the function WriteTIFFImage of coders/tiff.c, which allows an attacker to cause a denial of service or possibly information disclosure via a crafted image file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00043.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/4034-1/
- https://www.debian.org/security/2020/dsa-4712
- http://www.securityfocus.com/bid/108102
- https://github.com/ImageMagick/ImageMagick/issues/1555
