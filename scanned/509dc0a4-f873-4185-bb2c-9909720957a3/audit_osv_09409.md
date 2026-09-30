# [M] CVE-2016-9810

## Summary
Severity: Medium
Advisory: CVE-2016-9810
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/CVE-2016-9810
Type: osv

## Details
The gst_decode_chain_free_internal function in the flxdex decoder in gst-plugins-good in GStreamer before 1.10.2 allows remote attackers to cause a denial of service (invalid memory read and crash) via an invalid file, which triggers an incorrect unref call.

## References
- http://www.openwall.com/lists/oss-security/2016/12/01/2
- http://www.openwall.com/lists/oss-security/2016/12/05/8
- http://www.securityfocus.com/bid/95163
- https://access.redhat.com/errata/RHSA-2017:2060
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.2
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=774897
