# [H] CVE-2017-17426

## Summary
Severity: High
Advisory: CVE-2017-17426
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-05
Source: https://osv.dev/vulnerability/CVE-2017-17426
Type: osv

## Details
The malloc function in the GNU C Library (aka glibc or libc6) 2.26 could return a memory block that is too small if an attempt is made to allocate an object whose size is close to SIZE_MAX, potentially leading to a subsequent heap overflow. This occurs because the per-thread cache (aka tcache) feature enables a code path that lacks an integer overflow check.

## References
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=34697694e8a93b325b18f25f7dcded55d6baeaf6
- https://sourceware.org/bugzilla/show_bug.cgi?id=22375
