# [M] CVE-2016-9811

## Summary
Severity: Medium
Advisory: CVE-2016-9811
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/CVE-2016-9811
Type: osv

## Details
The windows_icon_typefind function in gst-plugins-base in GStreamer before 1.10.2, when G_SLICE is set to always-malloc, allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted ico file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UM7IXFGHV66KNWGWG6ZBDNKXD2UJL2VQ/
- http://www.debian.org/security/2017/dsa-3819
- http://www.openwall.com/lists/oss-security/2016/12/01/2
- http://www.openwall.com/lists/oss-security/2016/12/05/8
- http://www.securityfocus.com/bid/95161
- https://access.redhat.com/errata/RHSA-2017:2060
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.2
- https://lists.debian.org/debian-lts-announce/2020/02/msg00032.html
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=774902
