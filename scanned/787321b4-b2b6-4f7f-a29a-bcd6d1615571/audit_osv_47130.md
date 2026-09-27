# [H] CVE-2015-8983

## Summary
Severity: High
Advisory: CVE-2015-8983
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2015-8983
Type: osv

## Details
Integer overflow in the _IO_wstr_overflow function in libio/wstrops.c in the GNU C Library (aka glibc or libc6) before 2.22 allows context-dependent attackers to cause a denial of service (application crash) or possibly execute arbitrary code via vectors related to computing a size in bytes, which triggers a heap-based buffer overflow.

## References
- http://www.openwall.com/lists/oss-security/2017/02/14/9
- http://www.securityfocus.com/bid/72740
- https://www.sourceware.org/ml/libc-alpha/2015-08/msg00609.html
- http://www.openwall.com/lists/oss-security/2017/02/14/9
- http://www.openwall.com/lists/oss-security/2017/02/14/9
- https://sourceware.org/bugzilla/show_bug.cgi?id=17269
- https://sourceware.org/bugzilla/show_bug.cgi?id=17269
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=bdf1ff052a8e23d637f2c838fa5642d78fcedc33
