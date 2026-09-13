# [M] CVE-2017-14994

## Summary
Severity: Medium
Advisory: CVE-2017-14994
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-04
Source: https://osv.dev/vulnerability/CVE-2017-14994
Type: osv

## Details
ReadDCMImage in coders/dcm.c in GraphicsMagick 1.3.26 allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted DICOM image, related to the ability of DCM_ReadNonNativeImages to yield an image list with zero frames.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://usn.ubuntu.com/4232-1/
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=b3eca3eaa264
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- http://www.securityfocus.com/bid/101182
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://www.debian.org/security/2018/dsa-4321
- https://sourceforge.net/p/graphicsmagick/bugs/512/
- https://nandynarwhals.org/CVE-2017-14994/
