# [H] CVE-2017-6313

## Summary
Severity: High
Advisory: CVE-2017-6313
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2017-03-10
Source: https://osv.dev/vulnerability/CVE-2017-6313
Type: osv

## Details
Integer underflow in the load_resources function in io-icns.c in gdk-pixbuf allows context-dependent attackers to cause a denial of service (out-of-bounds read and program crash) via a crafted image entry size in an ICO file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SJF5ARFOX4BFUK6YCBKGAKBQYECO3AI2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VSAZ6UCKKXC5VOWXGWQHOX2ZBLLATIOT/
- http://mov.sx/2017/02/21/bug-hunting-gdk-pixbuf.html
- http://www.openwall.com/lists/oss-security/2017/02/26/1
- http://www.securityfocus.com/bid/96779
- https://lists.debian.org/debian-lts-announce/2019/12/msg00025.html
- https://security.gentoo.org/glsa/201709-08
- https://bugzilla.gnome.org/show_bug.cgi?id=779016
- http://www.openwall.com/lists/oss-security/2017/02/21/4
