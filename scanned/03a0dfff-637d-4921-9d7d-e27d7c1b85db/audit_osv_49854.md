# [C] CVE-2019-19950

## Summary
Severity: Critical
Advisory: CVE-2019-19950
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-24
Source: https://osv.dev/vulnerability/CVE-2019-19950
Type: osv

## Details
In GraphicsMagick 1.4 snapshot-20190403 Q8, there is a use-after-free in ThrowException and ThrowLoggedException of magick/error.c.

## References
- https://www.debian.org/security/2020/dsa-4640
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00064.html
- https://lists.debian.org/debian-lts-announce/2020/01/msg00029.html
- https://sourceforge.net/p/graphicsmagick/bugs/603/
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/44ab7f6c20b4
