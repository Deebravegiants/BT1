# [C] CVE-2017-18269

## Summary
Severity: Critical
Advisory: CVE-2017-18269
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2017-18269
Type: osv

## Details
An SSE2-optimized memmove implementation for i386 in sysdeps/i386/i686/multiarch/memcpy-sse2-unaligned.S in the GNU C Library (aka glibc or libc6) 2.21 through 2.27 does not correctly perform the overlapping memory check if the source memory range spans the middle of the address space, resulting in corrupt data being produced by the copy operation. This may disclose information to context-dependent attackers, or result in a denial of service, or, possibly, code execution.

## References
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=cd66c0e584c6d692bc8347b5e72723d02b8a8ada
- https://usn.ubuntu.com/4416-1/
- https://github.com/fingolfin/memmove-bug
- https://security.netapp.com/advisory/ntap-20190329-0001/
- https://security.netapp.com/advisory/ntap-20190401-0001/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22644
