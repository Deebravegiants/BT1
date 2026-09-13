# [M] CVE-2018-20376

## Summary
Severity: Medium
Advisory: CVE-2018-20376
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-23
Source: https://osv.dev/vulnerability/CVE-2018-20376
Type: osv

## Details
An issue was discovered in Tiny C Compiler (aka TinyCC or TCC) 0.9.27. Compiling a crafted source file leads to an 8 byte out of bounds write in the asm_parse_directive function in tccasm.c.

## References
- https://lists.nongnu.org/archive/html/tinycc-devel/2018-12/msg00013.html
