# [H] CVE-2019-11007

## Summary
Severity: High
Advisory: CVE-2019-11007
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-11007
Type: osv

## Details
In GraphicsMagick 1.4 snapshot-20190322 Q8, there is a heap-based buffer over-read in the ReadMNGImage function of coders/png.c, which allows attackers to cause a denial of service or information disclosure via an image colormap.

## References
- https://lists.debian.org/debian-lts-announce/2019/04/msg00015.html
- https://sourceforge.net/p/graphicsmagick/bugs/596/
- https://usn.ubuntu.com/4207-1/
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/40fc71472b98
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/86a9295e7c83
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00010.html
- https://www.debian.org/security/2020/dsa-4640
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00093.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00107.html
