# [M] CVE-2019-11470

## Summary
Severity: Medium
Advisory: CVE-2019-11470
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/CVE-2019-11470
Type: osv

## Details
The cineon parsing component in ImageMagick 7.0.8-26 Q16 allows attackers to cause a denial-of-service (uncontrolled resource consumption) by crafting a Cineon image with an incorrect claimed image size. This occurs because ReadCINImage in coders/cin.c lacks a check for insufficient image data in a file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00001.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00028.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://usn.ubuntu.com/4034-1/
- https://www.debian.org/security/2020/dsa-4712
- https://github.com/ImageMagick/ImageMagick/commit/e3cdce6fe12193f235b8c0ae5efe6880a25eb957
- https://github.com/ImageMagick/ImageMagick/issues/1472
