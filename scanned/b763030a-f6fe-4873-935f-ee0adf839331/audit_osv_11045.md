# [H] CVE-2017-5845

## Summary
Severity: High
Advisory: CVE-2017-5845
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2017-5845
Type: osv

## Details
The gst_avi_demux_parse_ncdt function in gst/avi/gstavidemux.c in gst-plugins-good in GStreamer before 1.10.3 allows remote attackers to cause a denial of service (invalid memory read and crash) via a ncdt sub-tag that "goes behind" the surrounding tag.

## References
- http://www.debian.org/security/2017/dsa-3820
- http://www.openwall.com/lists/oss-security/2017/02/01/7
- http://www.securityfocus.com/bid/96001
- https://access.redhat.com/errata/RHSA-2017:2060
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.3
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=777532
- http://www.openwall.com/lists/oss-security/2017/02/02/9
