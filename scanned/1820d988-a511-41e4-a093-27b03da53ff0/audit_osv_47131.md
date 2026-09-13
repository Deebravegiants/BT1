# [M] CVE-2015-8984

## Summary
Severity: Medium
Advisory: CVE-2015-8984
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2015-8984
Type: osv

## Details
The fnmatch function in the GNU C Library (aka glibc or libc6) before 2.22 might allow context-dependent attackers to cause a denial of service (application crash) via a malformed pattern, which triggers an out-of-bounds read.

## References
- http://www.openwall.com/lists/oss-security/2015/02/26/5
- http://www.openwall.com/lists/oss-security/2017/02/14/9
- http://www.securityfocus.com/bid/72789
- https://www.sourceware.org/ml/libc-alpha/2015-08/msg00609.html
- http://www.openwall.com/lists/oss-security/2015/02/26/5
- http://www.openwall.com/lists/oss-security/2017/02/14/9
- http://www.openwall.com/lists/oss-security/2015/02/26/5
- http://www.openwall.com/lists/oss-security/2017/02/14/9
- https://sourceware.org/bugzilla/show_bug.cgi?id=18032
- https://sourceware.org/bugzilla/show_bug.cgi?id=18032
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=4a28f4d55a6cc33474c0792fe93b5942d81bf185
