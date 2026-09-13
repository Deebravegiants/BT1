# [M] CVE-2019-12495

## Summary
Severity: Medium
Advisory: CVE-2019-12495
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-05-31
Source: https://osv.dev/vulnerability/CVE-2019-12495
Type: osv

## Details
An issue was discovered in Tiny C Compiler (aka TinyCC or TCC) 0.9.27. Compiling a crafted source file leads to a one-byte out-of-bounds write in the gsym_addr function in x86_64-gen.c. This occurs because tccasm.c mishandles section switches.

## References
- http://www.securityfocus.com/bid/108541
- https://repo.or.cz/tinycc.git/commit/d04ce7772c2bc2781ab2502e0b1f1964488814b5
- https://lists.nongnu.org/archive/html/tinycc-devel/2019-05/msg00044.html
