# [M] CVE-2016-9813

## Summary
Severity: Medium
Advisory: CVE-2016-9813
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/CVE-2016-9813
Type: osv

## Details
The _parse_pat function in the mpegts parser in GStreamer before 1.10.2 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted file.

## References
- https://www.exploit-db.com/exploits/42162/
- http://rhn.redhat.com/errata/RHSA-2017-0021.html
- http://www.debian.org/security/2017/dsa-3818
- http://www.openwall.com/lists/oss-security/2016/12/01/2
- http://www.openwall.com/lists/oss-security/2016/12/05/8
- http://www.securityfocus.com/bid/95158
- https://gstreamer.freedesktop.org/releases/1.10/#1.10.2
- https://security.gentoo.org/glsa/201705-10
- https://bugzilla.gnome.org/show_bug.cgi?id=775120
