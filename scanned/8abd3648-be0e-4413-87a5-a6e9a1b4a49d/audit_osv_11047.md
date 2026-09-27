# [H] CVE-2017-5847

## Summary
Severity: High
Advisory: CVE-2017-5847
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2017-5847
Type: osv

## Details
The gst_asf_demux_process_ext_content_desc function in gst/asfdemux/gstasfdemux.c in gst-plugins-ugly in GStreamer allows remote attackers to cause a denial of service (out-of-bounds heap read) via vectors involving extended content descriptors.

## References
- http://www.debian.org/security/2017/dsa-3821
- http://www.openwall.com/lists/oss-security/2017/02/01/7
- http://www.securityfocus.com/bid/96001
- https://lists.debian.org/debian-lts-announce/2020/05/msg00030.html
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=777955#c3
- http://www.openwall.com/lists/oss-security/2017/02/02/9
- https://github.com/GStreamer/gst-plugins-ugly/commit/d21017b52a585f145e8d62781bcc1c5fefc7ee37
