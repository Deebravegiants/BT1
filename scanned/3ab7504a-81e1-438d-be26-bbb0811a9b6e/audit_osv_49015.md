# [M] CVE-2018-20375

## Summary
Severity: Medium
Advisory: CVE-2018-20375
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-23
Source: https://osv.dev/vulnerability/CVE-2018-20375
Type: osv

## Details
An issue was discovered in Tiny C Compiler (aka TinyCC or TCC) 0.9.27. Compiling a crafted source file leads to an 8 byte out of bounds write in the sym_pop function in tccgen.c.

## References
- https://lists.nongnu.org/archive/html/tinycc-devel/2018-12/msg00014.html
