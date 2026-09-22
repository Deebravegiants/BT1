# [M] CVE-2018-19755

## Summary
Severity: Medium
Advisory: CVE-2018-19755
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-30
Source: https://osv.dev/vulnerability/CVE-2018-19755
Type: osv

## Details
There is an illegal address access at asm/preproc.c (function: is_mmacro) in Netwide Assembler (NASM) 2.14rc16 that will cause a denial of service (out-of-bounds array access) because a certain conversion can result in a negative integer.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392528
- https://repo.or.cz/nasm.git/commit/3079f7966dbed4497e36d5067cbfd896a90358cb
