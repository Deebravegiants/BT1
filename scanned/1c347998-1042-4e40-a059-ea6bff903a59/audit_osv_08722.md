# [H] CVE-2016-5417

## Summary
Severity: High
Advisory: CVE-2016-5417
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-5417
Type: osv

## Details
Memory leak in the __res_vinit function in the IPv6 name server management code in libresolv in GNU C Library (aka glibc or libc6) before 2.24 allows remote attackers to cause a denial of service (memory consumption) by leveraging partial initialization of internal resolver data structures.

## References
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Ba=commitdiff%3Bh=2212c1420c92a33b0e0bd9a34938c9814a56c0f7
- http://www.openwall.com/lists/oss-security/2016/08/02/5
- http://www.securityfocus.com/bid/92257
- https://www.sourceware.org/ml/libc-alpha/2016-08/msg00212.html
- https://sourceware.org/bugzilla/show_bug.cgi?id=19257
