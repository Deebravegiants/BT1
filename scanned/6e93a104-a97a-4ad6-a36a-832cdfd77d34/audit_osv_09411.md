# [H] CVE-2016-9812

## Summary
Severity: High
Advisory: CVE-2016-9812
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/CVE-2016-9812
Type: osv

## Details
The gst_mpegts_section_new function in the mpegts decoder in GStreamer before 1.10.2 allows remote attackers to cause a denial of service (out-of-bounds read) via a too small section.

## References
- http://www.openwall.com/lists/oss-security/2016/12/01/2
- http://www.openwall.com/lists/oss-security/2016/12/05/8
- http://www.securityfocus.com/bid/95160
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.2
- http://rhn.redhat.com/errata/RHSA-2017-0021.html
- http://www.debian.org/security/2017/dsa-3818
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=775048
