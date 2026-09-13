# [H] CVE-2021-3481

## Summary
Severity: High
Advisory: CVE-2021-3481
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2021-3481
Type: osv

## Details
A flaw was found in Qt. An out-of-bounds read vulnerability was found in QRadialFetchSimd in qt/qtbase/src/gui/painting/qdrawhelper_p.h in Qt/Qtbase. While rendering and displaying a crafted Scalable Vector Graphics (SVG) file this flaw may lead to an unauthorized memory access. The highest threat from this vulnerability is to data confidentiality and the application availability.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00028.html
- https://access.redhat.com/security/cve/CVE-2021-3481
- https://codereview.qt-project.org/c/qt/qtsvg/+/337646
- https://bugzilla.redhat.com/show_bug.cgi?id=1931444
- https://bugreports.qt.io/browse/QTBUG-91507
