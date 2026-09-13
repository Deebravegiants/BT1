# [H] CVE-2019-11008

## Summary
Severity: High
Advisory: CVE-2019-11008
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-11008
Type: osv

## Details
In GraphicsMagick 1.4 snapshot-20190322 Q8, there is a heap-based buffer overflow in the function WriteXWDImage of coders/xwd.c, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted image file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00093.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00107.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00055.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00015.html
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/d823d23a474b
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00010.html
- https://usn.ubuntu.com/4207-1/
- https://www.debian.org/security/2020/dsa-4640
- https://sourceforge.net/p/graphicsmagick/bugs/599/
