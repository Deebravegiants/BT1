# [H] CVE-2019-11598

## Summary
Severity: High
Advisory: CVE-2019-11598
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-04-29
Source: https://osv.dev/vulnerability/CVE-2019-11598
Type: osv

## Details
In ImageMagick 7.0.8-40 Q16, there is a heap-based buffer over-read in the function WritePNMImage of coders/pnm.c, which allows an attacker to cause a denial of service or possibly information disclosure via a crafted image file. This is related to SetGrayscaleImage in MagickCore/quantize.c.

## References
- https://usn.ubuntu.com/4034-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00001.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://www.debian.org/security/2020/dsa-4712
- http://www.securityfocus.com/bid/108102
- https://github.com/ImageMagick/ImageMagick/issues/1540
