# [M] CVE-2023-39129

## Summary
Severity: Medium
Advisory: CVE-2023-39129
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-07-25
Source: https://osv.dev/vulnerability/CVE-2023-39129
Type: osv

## Details
GNU gdb (GDB) 13.0.50.20220805-git was discovered to contain a heap use after free via the function add_pe_exported_sym() at /gdb/coff-pe-read.c.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=30640
