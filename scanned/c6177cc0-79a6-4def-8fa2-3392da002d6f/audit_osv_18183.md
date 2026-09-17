# [M] CVE-2020-24824

## Summary
Severity: Medium
Advisory: CVE-2020-24824
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-04
Source: https://osv.dev/vulnerability/CVE-2020-24824
Type: osv

## Details
A global buffer overflow issue in the dwarf::line_table::line_table function of Libelfin v0.3 allows attackers to cause a denial of service (DOS).

## References
- https://github.com/aclements/libelfin/issues/48
- https://github.com/xiaoxiongwang/function_bugs/tree/master/libelfin#global-buffer-overflow-in-function-dwarfline_tableline_table-at-dwarflinecc107
