# [C] CVE-2016-9635

## Summary
Severity: Critical
Advisory: CVE-2016-9635
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2016-9635
Type: osv

## Details
Heap-based buffer overflow in the flx_decode_delta_fli function in gst/flx/gstflxdec.c in the FLIC decoder in GStreamer before 1.10.2 allows remote attackers to execute arbitrary code or cause a denial of service (application crash) by providing a 'skip count' that goes beyond initialized buffer.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2975.html
- http://rhn.redhat.com/errata/RHSA-2017-0019.html
- http://rhn.redhat.com/errata/RHSA-2017-0020.html
- http://www.debian.org/security/2016/dsa-3723
- http://www.debian.org/security/2016/dsa-3724
- http://www.openwall.com/lists/oss-security/2016/11/24/2
- http://www.securityfocus.com/bid/94499
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.2
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=774834
- https://scarybeastsecurity.blogspot.com/2016/11/0day-exploit-advancing-exploitation.html
