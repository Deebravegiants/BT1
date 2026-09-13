# [M] CVE-2017-14528

## Summary
Severity: Medium
Advisory: CVE-2017-14528
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-18
Source: https://osv.dev/vulnerability/CVE-2017-14528
Type: osv

## Details
The TIFFSetProfiles function in coders/tiff.c in ImageMagick 7.0.6 has incorrect expectations about whether LibTIFF TIFFGetField return values imply that data validation has occurred, which allows remote attackers to cause a denial of service (use-after-free after an invalid call to TIFFSetField, and application crash) via a crafted file.

## References
- http://www.securityfocus.com/bid/100875
- https://lists.debian.org/debian-lts-announce/2021/01/msg00010.html
- http://bugzilla.maptools.org/show_bug.cgi?id=2730
- https://www.imagemagick.org/discourse-server/viewtopic.php?f=3&t=32560
