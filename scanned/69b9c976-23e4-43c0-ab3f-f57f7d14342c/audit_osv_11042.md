# [M] CVE-2017-5842

## Summary
Severity: Medium
Advisory: CVE-2017-5842
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2017-5842
Type: osv

## Details
The html_context_handle_element function in gst/subparse/samiparse.c in gst-plugins-base in GStreamer before 1.10.3 allows remote attackers to cause a denial of service (out-of-bounds write) via a crafted SMI file, as demonstrated by OneNote_Manager.smi.

## References
- http://www.debian.org/security/2017/dsa-3819
- http://www.openwall.com/lists/oss-security/2017/02/01/7
- http://www.securityfocus.com/bid/96001
- https://access.redhat.com/errata/RHSA-2017:2060
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.3
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=777502
- http://www.openwall.com/lists/oss-security/2017/02/02/9
