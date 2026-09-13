# [H] CVE-2017-6311

## Summary
Severity: High
Advisory: CVE-2017-6311
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-10
Source: https://osv.dev/vulnerability/CVE-2017-6311
Type: osv

## Details
gdk-pixbuf-thumbnailer.c in gdk-pixbuf allows context-dependent attackers to cause a denial of service (NULL pointer dereference and application crash) via vectors related to printing an error message.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SJF5ARFOX4BFUK6YCBKGAKBQYECO3AI2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VSAZ6UCKKXC5VOWXGWQHOX2ZBLLATIOT/
- http://mov.sx/2017/02/21/bug-hunting-gdk-pixbuf.html
- http://www.openwall.com/lists/oss-security/2017/02/26/1
- http://www.securityfocus.com/bid/96779
- https://security.gentoo.org/glsa/201709-08
- https://bugzilla.gnome.org/show_bug.cgi?id=778204
- http://www.openwall.com/lists/oss-security/2017/02/21/4
