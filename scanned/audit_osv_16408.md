# [H] CVE-2019-6488

## Summary
Severity: High
Advisory: CVE-2019-6488
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-18
Source: https://osv.dev/vulnerability/CVE-2019-6488
Type: osv

## Details
The string component in the GNU C Library (aka glibc or libc6) through 2.28, when running on the x32 architecture, incorrectly attempts to use a 64-bit register for size_t in assembly codes, which can lead to a segmentation fault or possibly unspecified other impact, as demonstrated by a crash in __memmove_avx_unaligned_erms in sysdeps/x86_64/multiarch/memmove-vec-unaligned-erms.S during a memcpy.

## References
- http://www.securityfocus.com/bid/106671
- https://security.gentoo.org/glsa/202006-04
- https://sourceware.org/bugzilla/show_bug.cgi?id=24097
