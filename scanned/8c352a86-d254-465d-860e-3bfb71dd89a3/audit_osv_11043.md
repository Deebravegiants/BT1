# [H] CVE-2017-5843

## Summary
Severity: High
Advisory: CVE-2017-5843
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2017-5843
Type: osv

## Details
Multiple use-after-free vulnerabilities in the (1) gst_mini_object_unref, (2) gst_tag_list_unref, and (3) gst_mxf_demux_update_essence_tracks functions in GStreamer before 1.10.3 allow remote attackers to cause a denial of service (crash) via vectors involving stream tags, as demonstrated by 02785736.mxf.

## References
- https://lists.debian.org/debian-lts-announce/2020/03/msg00038.html
- http://www.debian.org/security/2017/dsa-3818
- http://www.openwall.com/lists/oss-security/2017/02/01/7
- http://www.securityfocus.com/bid/96001
- https://access.redhat.com/errata/RHSA-2017:2060
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.3
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=777503
- http://www.openwall.com/lists/oss-security/2017/02/02/9
