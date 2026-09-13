# [H] CVE-2020-29573

## Summary
Severity: High
Advisory: CVE-2020-29573
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-06
Source: https://osv.dev/vulnerability/CVE-2020-29573
Type: osv

## Details
sysdeps/i386/ldbl2mpn.c in the GNU C Library (aka glibc or libc6) before 2.23 on x86 targets has a stack-based buffer overflow if the input to any of the printf family of functions is an 80-bit long double with a non-canonical bit pattern, as seen when passing a \x00\x04\x00\x00\x00\x00\x00\x00\x00\x04 value to sprintf. NOTE: the issue does not affect glibc by default in 2016 or later (i.e., 2.23 or later) because of commits made in 2015 for inlining of C99 math functions through use of GCC built-ins. In other words, the reference to 2.23 is intentional despite the mention of "Fixed for glibc 2.33" in the 26649 reference.

## References
- https://security.gentoo.org/glsa/202101-20
- https://security.netapp.com/advisory/ntap-20210122-0004/
- https://sourceware.org/bugzilla/show_bug.cgi?id=26649
- https://sourceware.org/pipermail/libc-alpha/2020-September/117779.html
