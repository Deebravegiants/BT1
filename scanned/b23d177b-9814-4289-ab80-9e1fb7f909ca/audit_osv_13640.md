# [M] CVE-2018-20662

## Summary
Severity: Medium
Advisory: CVE-2018-20662
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-03
Source: https://osv.dev/vulnerability/CVE-2018-20662
Type: osv

## Details
In Poppler 0.72.0, PDFDoc::setup in PDFDoc.cc allows attackers to cause a denial-of-service (application crash caused by Object.h SIGABRT, because of a wrong return value from PDFDoc::setup) by crafting a PDF file in which an xref data structure is mishandled during extractPDFSubtype processing.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6OSCOYM3AMFFBJWSBWY6VJVLNE5JD7YS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BI7NLDN2HUEU4ZW3D7XPHOAEGT2CKDRO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JQ6RABASMSIMMWMDZTP6ZWUWZPTBSVB5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZWP5XSUG6GNRI75NYKF53KIB2CZY6QQ6/
- https://access.redhat.com/errata/RHSA-2019:2022
- https://access.redhat.com/errata/RHSA-2019:2713
- https://gitlab.freedesktop.org/poppler/poppler/issues/706
- https://lists.debian.org/debian-lts-announce/2019/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00014.html
- https://usn.ubuntu.com/4042-1/
- https://gitlab.freedesktop.org/poppler/poppler/commit/9fd5ec0e6e5f763b190f2a55ceb5427cfe851d5f
