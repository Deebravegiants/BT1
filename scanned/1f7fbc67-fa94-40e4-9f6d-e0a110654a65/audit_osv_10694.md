# [M] CVE-2017-18267

## Summary
Severity: Medium
Advisory: CVE-2017-18267
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-10
Source: https://osv.dev/vulnerability/CVE-2017-18267
Type: osv

## Details
The FoFiType1C::cvtGlyph function in fofi/FoFiType1C.cc in Poppler through 0.64.0 allows remote attackers to cause a denial of service (infinite recursion) via a crafted PDF file, as demonstrated by pdftops.

## References
- https://lists.debian.org/debian-lts-announce/2020/07/msg00018.html
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3140
- https://access.redhat.com/errata/RHSA-2018:3505
- https://lists.debian.org/debian-lts-announce/2018/10/msg00024.html
- https://usn.ubuntu.com/3647-1/
- https://bugzilla.freedesktop.org/show_bug.cgi?id=103238
