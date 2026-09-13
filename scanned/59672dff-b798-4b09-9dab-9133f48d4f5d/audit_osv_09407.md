# [M] CVE-2016-9807

## Summary
Severity: Medium
Advisory: CVE-2016-9807
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/CVE-2016-9807
Type: osv

## Details
The flx_decode_chunks function in gst/flx/gstflxdec.c in GStreamer before 1.10.2 allows remote attackers to cause a denial of service (invalid memory read and crash) via a crafted FLIC file.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2975.html
- http://rhn.redhat.com/errata/RHSA-2017-0019.html
- http://rhn.redhat.com/errata/RHSA-2017-0020.html
- http://www.openwall.com/lists/oss-security/2016/12/01/2
- http://www.openwall.com/lists/oss-security/2016/12/05/8
- http://www.securityfocus.com/bid/95148
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.2
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=774859
- https://cgit.freedesktop.org/gstreamer/gst-plugins-good/commit/?id=153a8ae752c90d07190ef45803422a4f71ea8bff
