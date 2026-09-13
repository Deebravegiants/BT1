# [M] CVE-2017-7210

## Summary
Severity: Medium
Advisory: CVE-2017-7210
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-21
Source: https://osv.dev/vulnerability/CVE-2017-7210
Type: osv

## Details
objdump in GNU Binutils 2.28 is vulnerable to multiple heap-based buffer over-reads (of size 1 and size 8) while handling corrupt STABS enum type strings in a crafted object file, leading to program crash.

## References
- http://www.securityfocus.com/bid/96992
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=21157
