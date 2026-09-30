# [H] CVE-2017-5838

## Summary
Severity: High
Advisory: CVE-2017-5838
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2017-5838
Type: osv

## Details
The gst_date_time_new_from_iso8601_string function in gst/gstdatetime.c in GStreamer before 1.10.3 allows remote attackers to cause a denial of service (out-of-bounds heap read) via a malformed datetime string.

## References
- http://www.debian.org/security/2017/dsa-3822
- http://www.openwall.com/lists/oss-security/2017/02/01/7
- http://www.securityfocus.com/bid/96001
- https://access.redhat.com/errata/RHSA-2017:2060
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.3
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=777263
- http://www.openwall.com/lists/oss-security/2017/02/02/9
