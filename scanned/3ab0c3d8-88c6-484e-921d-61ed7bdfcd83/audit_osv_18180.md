# [M] CVE-2020-24821

## Summary
Severity: Medium
Advisory: CVE-2020-24821
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-04
Source: https://osv.dev/vulnerability/CVE-2020-24821
Type: osv

## Details
A vulnerability in the dwarf::cursor::skip_form function of Libelfin v0.3 allows attackers to cause a denial of service (DOS) through a segmentation fault via a crafted ELF file.

## References
- https://github.com/aclements/libelfin/issues/52
- https://github.com/xiaoxiongwang/function_bugs/tree/master/libelfin#segv-in-function-dwarfcursorskip_form-at-dwarfcursorcc191
