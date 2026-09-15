# [M] CVE-2019-11472

## Summary
Severity: Medium
Advisory: CVE-2019-11472
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/CVE-2019-11472
Type: osv

## Details
ReadXWDImage in coders/xwd.c in the XWD image parsing component of ImageMagick 7.0.8-41 Q16 allows attackers to cause a denial-of-service (divide-by-zero error) by crafting an XWD image file in which the header indicates neither LSB first nor MSB first.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00001.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://usn.ubuntu.com/4034-1/
- https://www.debian.org/security/2020/dsa-4712
- https://github.com/ImageMagick/ImageMagick6/commit/f663dfb8431c97d95682a2b533cca1c8233d21b4
- https://github.com/ImageMagick/ImageMagick/issues/1546
