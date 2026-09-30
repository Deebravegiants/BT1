# [M] CVE-2019-12974

## Summary
Severity: Medium
Advisory: CVE-2019-12974
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-26
Source: https://osv.dev/vulnerability/CVE-2019-12974
Type: osv

## Details
A NULL pointer dereference in the function ReadPANGOImage in coders/pango.c and the function ReadVIDImage in coders/vid.c in ImageMagick 7.0.8-34 allows remote attackers to cause a denial of service via a crafted image.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- http://www.securityfocus.com/bid/108913
- https://lists.debian.org/debian-lts-announce/2019/08/msg00021.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://github.com/ImageMagick/ImageMagick/issues/1515
