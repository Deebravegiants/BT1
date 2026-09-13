# [H] CVE-2019-9200

## Summary
Severity: High
Advisory: CVE-2019-9200
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-26
Source: https://osv.dev/vulnerability/CVE-2019-9200
Type: osv

## Details
A heap-based buffer underwrite exists in ImageStream::getLine() located at Stream.cc in Poppler 0.74.0 that can (for example) be triggered by sending a crafted PDF file to the pdfimages binary. It allows an attacker to cause Denial of Service (Segmentation fault) or possibly have unspecified other impact.

## References
- https://lists.debian.org/debian-lts-announce/2020/07/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6OSCOYM3AMFFBJWSBWY6VJVLNE5JD7YS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JQ6RABASMSIMMWMDZTP6ZWUWZPTBSVB5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZWP5XSUG6GNRI75NYKF53KIB2CZY6QQ6/
- https://usn.ubuntu.com/4042-1/
- http://www.securityfocus.com/bid/107172
- https://access.redhat.com/errata/RHSA-2019:2022
- https://access.redhat.com/errata/RHSA-2019:2713
- https://lists.debian.org/debian-lts-announce/2019/03/msg00008.html
- https://usn.ubuntu.com/3905-1/
- https://gitlab.freedesktop.org/poppler/poppler/issues/728
- https://research.loginsoft.com/bugs/heap-based-buffer-underwrite-in-imagestreamgetline-poppler-0-74-0/
