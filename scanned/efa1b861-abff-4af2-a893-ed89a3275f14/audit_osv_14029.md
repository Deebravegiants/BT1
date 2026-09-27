# [C] CVE-2018-6485

## Summary
Severity: Critical
Advisory: CVE-2018-6485
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-01
Source: https://osv.dev/vulnerability/CVE-2018-6485
Type: osv

## Details
An integer overflow in the implementation of the posix_memalign in memalign functions in the GNU C Library (aka glibc or libc6) 2.26 and earlier could cause these functions to return a pointer to a heap area that is too small, potentially leading to heap corruption.

## References
- https://usn.ubuntu.com/4218-1/
- https://usn.ubuntu.com/4416-1/
- http://www.securityfocus.com/bid/102912
- https://access.redhat.com/errata/RHBA-2019:0327
- https://security.netapp.com/advisory/ntap-20190404-0003/
- http://bugs.debian.org/878159
- https://sourceware.org/bugzilla/show_bug.cgi?id=22343
- https://access.redhat.com/errata/RHSA-2018:3092
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
