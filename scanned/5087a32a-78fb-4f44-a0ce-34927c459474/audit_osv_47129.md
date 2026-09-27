# [H] CVE-2015-8982

## Summary
Severity: High
Advisory: CVE-2015-8982
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2015-8982
Type: osv

## Details
Integer overflow in the strxfrm function in the GNU C Library (aka glibc or libc6) before 2.21 allows context-dependent attackers to cause a denial of service (crash) or possibly execute arbitrary code via a long string, which triggers a stack-based buffer overflow.

## References
- http://www.openwall.com/lists/oss-security/2015/02/13/3
- http://www.openwall.com/lists/oss-security/2017/02/14/9
- http://www.securityfocus.com/bid/72602
- http://www.openwall.com/lists/oss-security/2015/02/13/3
- http://www.openwall.com/lists/oss-security/2017/02/14/9
- http://www.openwall.com/lists/oss-security/2015/02/13/3
- http://www.openwall.com/lists/oss-security/2017/02/14/9
- https://sourceware.org/bugzilla/show_bug.cgi?id=16009
- https://sourceware.org/bugzilla/show_bug.cgi?id=16009
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=0f9e585480ed
