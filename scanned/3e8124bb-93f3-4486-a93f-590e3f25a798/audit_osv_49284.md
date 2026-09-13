# [M] CVE-2018-9018

## Summary
Severity: Medium
Advisory: CVE-2018-9018
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-25
Source: https://osv.dev/vulnerability/CVE-2018-9018
Type: osv

## Details
In GraphicsMagick 1.3.28, there is a divide-by-zero in the ReadMNGImage function of coders/png.c. Remote attackers could leverage this vulnerability to cause a crash and denial of service via a crafted mng file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3IYH7QSNXXOIDFTYLY455ANZ3JWQ7FCS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FS76VNCFL3FVRMGXQEMHBOKA7EE46BTS/
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/103526
- https://lists.debian.org/debian-lts-announce/2018/03/msg00025.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://sourceforge.net/p/graphicsmagick/bugs/554/
