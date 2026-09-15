# [C] CVE-2019-11005

## Summary
Severity: Critical
Advisory: CVE-2019-11005
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-11005
Type: osv

## Details
In GraphicsMagick 1.4 snapshot-20190322 Q8, there is a stack-based buffer overflow in the function SVGStartElement of coders/svg.c, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a quoted font family value.

## References
- https://usn.ubuntu.com/4207-1/
- https://www.debian.org/security/2020/dsa-4640
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/b6fb77d7d54d
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00093.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00107.html
- https://sourceforge.net/p/graphicsmagick/bugs/600/
