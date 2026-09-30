# [H] CVE-2016-9445

## Summary
Severity: High
Advisory: CVE-2016-9445
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-9445
Type: osv

## Details
Integer overflow in the vmnc decoder in the gstreamer allows remote attackers to cause a denial of service (crash) via large width and height values, which triggers a buffer overflow.

## References
- http://www.openwall.com/lists/oss-security/2016/11/18/12
- http://www.openwall.com/lists/oss-security/2016/11/18/13
- http://www.securityfocus.com/bid/94421
- https://cgit.freedesktop.org/gstreamer/gst-plugins-bad/commit/gst/vmnc/vmncdec.c?id=4cb1bcf1422bbcd79c0f683edb7ee85e3f7a31fe
- http://rhn.redhat.com/errata/RHSA-2016-2974.html
- http://rhn.redhat.com/errata/RHSA-2017-0018.html
- http://rhn.redhat.com/errata/RHSA-2017-0021.html
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=774533
- https://scarybeastsecurity.blogspot.de/2016/11/0day-poc-risky-design-decisions-in.html
