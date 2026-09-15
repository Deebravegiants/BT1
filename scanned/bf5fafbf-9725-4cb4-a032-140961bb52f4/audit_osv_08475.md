# [H] CVE-2016-3706

## Summary
Severity: High
Advisory: CVE-2016-3706
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-10
Source: https://osv.dev/vulnerability/CVE-2016-3706
Type: osv

## Details
Stack-based buffer overflow in the getaddrinfo function in sysdeps/posix/getaddrinfo.c in the GNU C Library (aka glibc or libc6) allows remote attackers to cause a denial of service (crash) via vectors involving hostent conversion. NOTE: this vulnerability exists because of an incomplete fix for CVE-2013-4458.

## References
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=4ab2ab03d4351914ee53248dc5aef4a8c88ff8b9
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00030.html
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00039.html
- http://www-01.ibm.com/support/docview.wss?uid=swg21995039
- http://www.securityfocus.com/bid/102073
- http://www.securityfocus.com/bid/88440
- https://source.android.com/security/bulletin/2017-12-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=20010
