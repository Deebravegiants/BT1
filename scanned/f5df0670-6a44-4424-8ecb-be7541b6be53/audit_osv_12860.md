# [M] CVE-2018-15834

## Summary
Severity: Medium
Advisory: CVE-2018-15834
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-12
Source: https://osv.dev/vulnerability/CVE-2018-15834
Type: osv

## Details
In radare2 before 2.9.0, a heap overflow vulnerability exists in the read_module_referenced_functions function in libr/anal/flirt.c via a crafted flirt signature file.

## References
- https://github.com/radare/radare2/issues/11274
- https://github.com/radare/radare2/pull/11300
