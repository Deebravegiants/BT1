# [M] CVE-2018-19842

## Summary
Severity: Medium
Advisory: CVE-2018-19842
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-04
Source: https://osv.dev/vulnerability/CVE-2018-19842
Type: osv

## Details
getToken in libr/asm/p/asm_x86_nz.c in radare2 before 3.1.0 allows attackers to cause a denial of service (stack-based buffer over-read) via crafted x86 assembly data, as demonstrated by rasm2.

## References
- https://github.com/radare/radare2/commit/66191f780863ea8c66ace4040d0d04a8842e8432
- https://github.com/radare/radare2/issues/12239
