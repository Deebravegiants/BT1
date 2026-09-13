# [H] CVE-2016-9808

## Summary
Severity: High
Advisory: CVE-2016-9808
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/CVE-2016-9808
Type: osv

## Details
The FLIC decoder in GStreamer before 1.10.2 allows remote attackers to cause a denial of service (out-of-bounds write and crash) via a crafted series of skip and count pairs.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2975.html
- http://rhn.redhat.com/errata/RHSA-2017-0019.html
- http://rhn.redhat.com/errata/RHSA-2017-0020.html
- http://www.openwall.com/lists/oss-security/2016/12/01/2
- http://www.openwall.com/lists/oss-security/2016/12/05/8
- http://www.securityfocus.com/bid/95446
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.2
- https://security.gentoo.org/glsa/201705-10
- https://scarybeastsecurity.blogspot.com/2016/11/0day-poc-incorrect-fix-for-gstreamer.html
