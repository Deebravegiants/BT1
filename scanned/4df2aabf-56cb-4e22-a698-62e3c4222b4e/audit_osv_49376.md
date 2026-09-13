# [H] CVE-2019-11505

## Summary
Severity: High
Advisory: CVE-2019-11505
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/CVE-2019-11505
Type: osv

## Details
In GraphicsMagick from version 1.3.8 to 1.4 snapshot-20190403 Q8, there is a heap-based buffer overflow in the function WritePDBImage of coders/pdb.c, which allows an attacker to cause a denial of service or possibly have unspecified other impact via a crafted image file. This is related to MagickBitStreamMSBWrite in magick/bit_stream.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00001.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00027.html
- https://usn.ubuntu.com/4207-1/
- https://www.debian.org/security/2020/dsa-4640
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00021.html
- http://www.securityfocus.com/bid/108063
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/85f5bdcd246a
- https://sourceforge.net/p/graphicsmagick/bugs/605/
