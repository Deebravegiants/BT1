# [H] CVE-2016-9446

## Summary
Severity: High
Advisory: CVE-2016-9446
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-9446
Type: osv

## Details
The vmnc decoder in the gstreamer does not initialize the render canvas, which allows remote attackers to obtain sensitive information as demonstrated by thumbnailing a simple 1 frame vmnc movie that does not draw to the allocated render canvas.

## References
- http://www.openwall.com/lists/oss-security/2016/11/18/12
- http://www.openwall.com/lists/oss-security/2016/11/18/13
- http://www.securityfocus.com/bid/94423
- https://cgit.freedesktop.org/gstreamer/gst-plugins-bad/commit/gst/vmnc/vmncdec.c?id=4cb1bcf1422bbcd79c0f683edb7ee85e3f7a31fe
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UM7IXFGHV66KNWGWG6ZBDNKXD2UJL2VQ/
- https://access.redhat.com/errata/RHSA-2017:2060
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=774533
- https://scarybeastsecurity.blogspot.de/2016/11/0day-poc-risky-design-decisions-in.html
