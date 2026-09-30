# [M] CVE-2020-17507

## Summary
Severity: Medium
Advisory: CVE-2020-17507
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2020-08-12
Source: https://osv.dev/vulnerability/CVE-2020-17507
Type: osv

## Details
An issue was discovered in Qt through 5.12.9, and 5.13.x through 5.15.x before 5.15.1. read_xbm_body in gui/image/qxbmhandler.cpp has a buffer over-read.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00071.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00073.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00090.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00104.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00105.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/426FCC6JNK4JUEX5QHJQDYQ6MUVQ3E6P/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NBPZVZNEYXGATTXM4WOE7OQ55VAKPVD6/
- https://codereview.qt-project.org/c/qt/qtbase/+/308496
- https://lists.debian.org/debian-lts-announce/2020/09/msg00023.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00024.html
- https://security.gentoo.org/glsa/202009-04
- https://codereview.qt-project.org/c/qt/qtbase/+/308436
- https://codereview.qt-project.org/c/qt/qtbase/+/308495
