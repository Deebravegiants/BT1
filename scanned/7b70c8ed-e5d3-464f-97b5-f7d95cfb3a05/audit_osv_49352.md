# [H] CVE-2019-11009

## Summary
Severity: High
Advisory: CVE-2019-11009
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-11009
Type: osv

## Details
In GraphicsMagick 1.4 snapshot-20190322 Q8, there is a heap-based buffer over-read in the function ReadXWDImage of coders/xwd.c, which allows attackers to cause a denial of service or information disclosure via a crafted image file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00021.html
- https://usn.ubuntu.com/4207-1/
- https://lists.debian.org/debian-lts-announce/2019/04/msg00015.html
- https://www.debian.org/security/2020/dsa-4640
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/7cff2b1792de
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00093.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00107.html
- https://sourceforge.net/p/graphicsmagick/bugs/597/
