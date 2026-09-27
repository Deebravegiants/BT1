# [M] CVE-2018-20535

## Summary
Severity: Medium
Advisory: CVE-2018-20535
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-28
Source: https://osv.dev/vulnerability/CVE-2018-20535
Type: osv

## Details
There is a use-after-free at asm/preproc.c (function pp_getline) in Netwide Assembler (NASM) 2.14rc16 that will cause a denial of service during a line-number increment attempt.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392530
