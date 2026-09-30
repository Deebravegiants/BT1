# [H] CVE-2018-19870

## Summary
Severity: High
Advisory: CVE-2018-19870
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-26
Source: https://osv.dev/vulnerability/CVE-2018-19870
Type: osv

## Details
An issue was discovered in Qt before 5.11.3. A malformed GIF image causes a NULL pointer dereference in QGifHandler resulting in a segmentation fault.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00014.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00023.html
- https://usn.ubuntu.com/4003-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00080.html
- https://access.redhat.com/errata/RHSA-2019:2135
- https://access.redhat.com/errata/RHSA-2019:3390
- https://blog.qt.io/blog/2018/12/04/qt-5-11-3-released-important-security-updates/
- https://lists.debian.org/debian-lts-announce/2019/01/msg00004.html
- https://www.debian.org/security/2019/dsa-4374
- https://codereview.qt-project.org/#/c/235998/
