# [H] CVE-2019-20352

## Summary
Severity: High
Advisory: CVE-2019-20352
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2020-01-06
Source: https://osv.dev/vulnerability/CVE-2019-20352
Type: osv

## Details
In Netwide Assembler (NASM) 2.15rc0, a heap-based buffer over-read occurs (via a crafted .asm file) in set_text_free when called from expand_one_smacro in asm/preproc.c.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392636
