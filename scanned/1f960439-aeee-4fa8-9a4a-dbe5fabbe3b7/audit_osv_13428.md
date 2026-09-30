# [M] CVE-2018-19843

## Summary
Severity: Medium
Advisory: CVE-2018-19843
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-04
Source: https://osv.dev/vulnerability/CVE-2018-19843
Type: osv

## Details
opmov in libr/asm/p/asm_x86_nz.c in radare2 before 3.1.0 allows attackers to cause a denial of service (buffer over-read) via crafted x86 assembly data, as demonstrated by rasm2.

## References
- https://github.com/radare/radare2/commit/f17bfd9f1da05f30f23a4dd05e9d2363e1406948
- https://github.com/radare/radare2/issues/12242
