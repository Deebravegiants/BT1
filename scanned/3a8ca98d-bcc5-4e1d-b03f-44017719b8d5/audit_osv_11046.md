# [M] CVE-2017-5846

## Summary
Severity: Medium
Advisory: CVE-2017-5846
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2017-5846
Type: osv

## Details
The gst_asf_demux_process_ext_stream_props function in gst/asfdemux/gstasfdemux.c in gst-plugins-ugly in GStreamer before 1.10.3 allows remote attackers to cause a denial of service (invalid memory read and crash) via vectors related to the number of languages in a video file.

## References
- https://lists.debian.org/debian-lts-announce/2020/05/msg00030.html
- http://www.debian.org/security/2017/dsa-3821
- http://www.openwall.com/lists/oss-security/2017/02/01/7
- http://www.openwall.com/lists/oss-security/2017/02/02/9
- http://www.securityfocus.com/bid/96001
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.3
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=777937
