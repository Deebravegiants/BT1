# [C] CVE-2017-9053

## Summary
Severity: Critical
Advisory: CVE-2017-9053
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9053
Type: osv

## Details
An issue, also known as DW201703-005, was discovered in libdwarf 2017-03-21. A heap-based buffer over-read in _dwarf_read_loc_expr_op() is due to a failure to check a pointer for being in bounds (in a few places in this function).

## References
- https://www.prevanders.net/dwarfbug.html
