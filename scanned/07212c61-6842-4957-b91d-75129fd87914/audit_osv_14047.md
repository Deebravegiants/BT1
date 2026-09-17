# [C] CVE-2018-6551

## Summary
Severity: Critical
Advisory: CVE-2018-6551
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/CVE-2018-6551
Type: osv

## Details
The malloc implementation in the GNU C Library (aka glibc or libc6), from version 2.24 to 2.26 on powerpc, and only in version 2.26 on i386, did not properly handle malloc calls with arguments close to SIZE_MAX and could return a pointer to a heap region that is smaller than requested, eventually leading to heap corruption.

## References
- https://sourceware.org/git/?p=glibc.git%3Ba=commit%3Bh=8e448310d74b283c5cd02b9ed7fb997b47bf9b22
- https://security.netapp.com/advisory/ntap-20190404-0003/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22774
