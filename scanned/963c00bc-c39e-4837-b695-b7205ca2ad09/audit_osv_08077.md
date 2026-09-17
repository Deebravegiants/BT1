# [M] CVE-2016-10198

## Summary
Severity: Medium
Advisory: CVE-2016-10198
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2016-10198
Type: osv

## Details
The gst_aac_parse_sink_setcaps function in gst/audioparsers/gstaacparse.c in gst-plugins-good in GStreamer before 1.10.3 allows remote attackers to cause a denial of service (invalid memory read and crash) via a crafted audio file.

## References
- https://lists.debian.org/debian-lts-announce/2020/05/msg00029.html
- http://www.debian.org/security/2017/dsa-3820
- http://www.openwall.com/lists/oss-security/2017/02/01/7
- http://www.securityfocus.com/bid/96001
- https://access.redhat.com/errata/RHSA-2017:2060
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.3
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=775450
- http://www.openwall.com/lists/oss-security/2017/02/02/9
