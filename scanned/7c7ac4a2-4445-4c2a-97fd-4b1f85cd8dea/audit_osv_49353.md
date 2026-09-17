# [M] CVE-2019-11010

## Summary
Severity: Medium
Advisory: CVE-2019-11010
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-11010
Type: osv

## Details
In GraphicsMagick 1.4 snapshot-20190322 Q8, there is a memory leak in the function ReadMPCImage of coders/mpc.c, which allows attackers to cause a denial of service via a crafted image file.

## References
- https://usn.ubuntu.com/4207-1/
- https://lists.debian.org/debian-lts-announce/2019/04/msg00015.html
- https://www.debian.org/security/2020/dsa-4640
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00093.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00107.html
- https://sourceforge.net/p/graphicsmagick/bugs/601/
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/a348d9661019
