# [M] CVE-2019-9754

## Summary
Severity: Medium
Advisory: CVE-2019-9754
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-03-13
Source: https://osv.dev/vulnerability/CVE-2019-9754
Type: osv

## Details
An issue was discovered in Tiny C Compiler (aka TinyCC or TCC) 0.9.27. Compiling a crafted source file leads to an 1 byte out of bounds write in the end_macro function in tccpp.c.

## References
- https://lists.nongnu.org/archive/html/tinycc-devel/2019-03/msg00038.html
