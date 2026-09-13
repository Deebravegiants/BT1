# [H] CVE-2017-15565

## Summary
Severity: High
Advisory: CVE-2017-15565
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-17
Source: https://osv.dev/vulnerability/CVE-2017-15565
Type: osv

## Details
In Poppler 0.59.0, a NULL Pointer Dereference exists in the GfxImageColorMap::getGrayLine() function in GfxState.cc via a crafted PDF document.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00023.html
- https://www.debian.org/security/2018/dsa-4079
- https://bugs.freedesktop.org/show_bug.cgi?id=103016
