# [M] CVE-2017-6314

## Summary
Severity: Medium
Advisory: CVE-2017-6314
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-10
Source: https://osv.dev/vulnerability/CVE-2017-6314
Type: osv

## Details
The make_available_at_least function in io-tiff.c in gdk-pixbuf allows context-dependent attackers to cause a denial of service (infinite loop) via a large TIFF file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SJF5ARFOX4BFUK6YCBKGAKBQYECO3AI2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VSAZ6UCKKXC5VOWXGWQHOX2ZBLLATIOT/
- http://mov.sx/2017/02/21/bug-hunting-gdk-pixbuf.html
- http://www.securityfocus.com/bid/96779
- https://lists.debian.org/debian-lts-announce/2019/12/msg00025.html
- https://security.gentoo.org/glsa/201709-08
- https://bugzilla.gnome.org/show_bug.cgi?id=779020
- http://www.openwall.com/lists/oss-security/2017/02/21/4
- http://www.openwall.com/lists/oss-security/2017/02/26/1
